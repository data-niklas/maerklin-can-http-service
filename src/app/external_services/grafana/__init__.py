import sys
import os
import subprocess
import signal
import requests
import time
from requests.utils import requote_uri
# Plugins needed: grafana-cli --pluginUrl https://github.com/cloudspout/cloudspout-button-panel/releases/download/7.0.23/cloudspout-button-panel.zip plugins install cloudspout-button-panel
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config import get_settings

settings = get_settings()

PORT = settings.grafana_port
HOMEFOLDER = settings.grafana_dir
API_KEY = settings.grafana_api_key
# Only works if a sqlite3 database was used and the path starts with an 'sqlite:///'
DATASOURCE_PATH = settings.high_level_db_dump_database.split("///")[1]


CAN_BASE_URL = f"http://{settings.can_host}:{settings.can_port}/"
CAN_GET_HASH = CAN_BASE_URL + "general/hash"
CAN_LOC_LIST = CAN_BASE_URL + "lok/list"

DATABASE_PORT = settings.database_port
DATABASE_HOST = settings.database_host

CONFIG_FILE = os.path.join(HOMEFOLDER, "conf", "defaults.ini")
CONFIG_TEMPLATE_FILE =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.ini.template")
VIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views")
AUTHORIZATION_HEADER = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

CAN_HASH = ""

def apply_config(port):
    os.system(f'sed -E "s/http_port = [0-9]+$/http_port = {port}/g" {CONFIG_TEMPLATE_FILE} > {CONFIG_FILE}')

active_process = None
def start_grafana():
    global active_process
    active_process = subprocess.Popen(["grafana-server", "--homepath", HOMEFOLDER], stdout=subprocess.DEVNULL)
    def signal_handler(sig, frame):
        active_process.terminate()
        active_process.wait()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print(f'Serving grafana on http://localhost:{PORT}')

def apply_file(file, url, modifier_cb):
    with open(file, 'r', encoding="utf-8") as f:
        data = f.read()
        data = modifier_cb(data)
        print(url)
        print(data)
        result = requests.post(url, data=data, headers=AUTHORIZATION_HEADER)
        print(result.content)

def apply_datasource(file):
    apply_file(file, f'http://localhost:{PORT}/api/datasources', lambda data: data.replace("DBPATH", DATASOURCE_PATH))


def apply_dashboard(file, preprocess_cb):
    apply_file(file, f'http://localhost:{PORT}/api/dashboards/db', lambda data: """{
            "dashboard": """ + preprocess_cb(data) +  """,
            "overwrite": true
    }""")

def get_hash():
    return str(requests.get(CAN_GET_HASH).json())

def scan_for_locs():
    return requests.get(CAN_LOC_LIST, headers={'x-can-hash': CAN_HASH}).json()

def apply_loc(loc, maxFuelA, maxFuelB, maxSand):
    file = os.path.join(VIEWS_DIR, "loc.json")
    loc_map = dict()
    loc_map["LOC_ID"] = str(loc["loc_id"])
    loc_map["LOC_MFXUID"] = str(loc["mfxuid"])
    loc_map["LOC_NAME"] = loc["vorname"] + " " + loc["name"]
    loc_map["LOC_FUELA_MAX"] = str(maxFuelA)
    loc_map["LOC_FUELB_MAX"] = str(maxFuelA)
    loc_map["LOC_SAND_MAX"] = str(maxSand)

    def map_data(data):
        for k in loc_map:
            data = data.replace(k, loc_map[k])
        return data
    apply_dashboard(file, map_data)

DEFAULT_FUELA_MAX = 100
DEFAULT_FUELB_MAX = 100
DEFAULT_SAND_MAX = 100

def read_lok_usage(mfxuid):
    filter = requote_uri(f'mfxuid eq {mfxuid}')
    url = f'http://{DATABASE_HOST}:{DATABASE_PORT}/getConfigUsageMessage?filter={filter}&limit=1'
    usage_data = requests.get(url).json()
    if usage_data.total == 0:
        return DEFAULT_FUELA_MAX, DEFAULT_FUELB_MAX, DEFAULT_SAND_MAX
    
    maxFuelA = usage_data.items[0].maxFuelA
    maxFuelB = usage_data.items[0].maxFuelB
    maxSand = usage_data.items[0].maxSand

    if maxFuelA is None:
        maxFuelA = DEFAULT_FUELA_MAX
    if maxFuelB is None:
        maxFuelB = DEFAULT_FUELB_MAX
    if maxSand is None:
        maxSand = DEFAULT_SAND_MAX

    return maxFuelA, maxFuelB, maxSand


def update():
    for loc in scan_for_locs():
        maxFuelA, maxFuelB, maxSand = read_lok_usage(loc["mfxuid"])
        apply_loc(loc, maxFuelA, maxFuelB, maxSand)

apply_config(PORT)
start_grafana()
# Let grafana initialize the server
time.sleep(5)

apply_datasource(os.path.join(VIEWS_DIR, "datasource.json"))
apply_dashboard(os.path.join(VIEWS_DIR, "general.json"), lambda data: data)

CAN_HASH = get_hash()
while True:
    update()
    time.sleep(300)