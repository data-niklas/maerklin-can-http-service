import sys
import os
import subprocess
import signal
import requests
from requests.utils import requote_uri
import time
from functools import lru_cache
# Plugins needed: https://github.com/cloudspout/cloudspout-button-panel 
# Installation: grafana-cli --pluginUrl https://github.com/cloudspout/cloudspout-button-panel/releases/download/7.0.23/cloudspout-button-panel.zip plugins install cloudspout-button-panel
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(CURRENT_DIR))))
from config import get_settings

settings = get_settings()

PORT = settings.grafana_port
HOMEFOLDER = settings.grafana_dir
API_KEY = settings.grafana_api_key
# Only works if a sqlite3 database was used and the path starts with an 'sqlite:///'
DATASOURCE_PATH = settings.db_dump_database.split("///")[1]
DATASOURCE_UID = "yyAw0-bnz"
DATASOURCE_TYPE = "frser-sqlite-datasource"

CAN_BASE_URL = f"http://{settings.can_host}:{settings.can_port}/"
CAN_GET_HASH = CAN_BASE_URL + "general/hash"
CAN_LOC_LIST = CAN_BASE_URL + "lok/list"

DATABASE_PORT = settings.database_read_port
DATABASE_HOST = settings.database_read_host

GRAFANA_UPDATE_INTERVAL = settings.grafana_update_interval

CONFIG_FILE = os.path.join(HOMEFOLDER, "conf", "defaults.ini")
CONFIG_TEMPLATE_FILE =  os.path.join(CURRENT_DIR, "defaults.ini.template")
VIEWS_DIR = os.path.join(CURRENT_DIR, "views")
AUTHORIZATION_HEADER = {'Authorization': f'Bearer {API_KEY}', 'Content-Type': 'application/json'}

DEFAULT_FUELA_MAX = 255
DEFAULT_FUELB_MAX = 255
DEFAULT_SAND_MAX = 255

DISTANCE_MAX = 1024 * settings.resample_interval

LOG_LIMIT = 200

def apply_config(port):
    os.system(f'sed -E "s/http_port = [0-9]+$/http_port = {port}/g" {CONFIG_TEMPLATE_FILE} > {CONFIG_FILE}')

def start_grafana():
    active_process = subprocess.Popen(["grafana-server", "--homepath", HOMEFOLDER], stdout=subprocess.DEVNULL)
    def signal_handler(sig, frame):
        active_process.terminate()
        active_process.wait()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    print(f'Serving grafana on http://localhost:{PORT}')

def apply_template(template_path, url, fill_template_callback):
    with open(template_path, 'r', encoding="utf-8") as f:
        template = f.read()
        template = fill_template_callback(template)
        print(url)
        result = requests.post(url, data=template, headers=AUTHORIZATION_HEADER)
        print(result.content)

def apply_datasource(datasource_template_path, datasource_uid):
    apply_template(
        datasource_template_path,
        f'http://localhost:{PORT}/api/datasources', 
        lambda data: data.replace("DBPATH", DATASOURCE_PATH).replace("DATASOURCE_UID", datasource_uid)
    )


def apply_dashboard(dashboard_template_path, fill_dashboard_callback):
    apply_template(dashboard_template_path, f'http://localhost:{PORT}/api/dashboards/db', lambda data: """{
            "dashboard": """ + fill_dashboard_callback(data) +  """,
            "overwrite": true
    }""")

@lru_cache
def get_hash():
    return str(requests.get(CAN_GET_HASH).json())

def get_locs():
    res = requests.get(CAN_LOC_LIST, headers={'x-can-hash': get_hash()}).json()
    if isinstance(res, list):
        return res
    return None

def apply_loc(loc, max_fuel_a, max_fuel_b, max_sand):
    loc_template_path = os.path.join(VIEWS_DIR, "loc.json.template")
    loc_map = dict()
    loc_map["LOC_ID"] = str(loc["loc_id"])
    loc_map["LOC_MFXUID"] = str(loc["mfxuid"])
    loc_map["LOC_NAME"] = loc["name"]
    loc_map["LOC_FUELA_MAX"] = str(max_fuel_a)
    loc_map["LOC_FUELB_MAX"] = str(max_fuel_b)
    loc_map["LOC_SAND_MAX"] = str(max_sand)
    loc_map["DATASOURCE_UID"] = DATASOURCE_UID
    loc_map["DATASOURCE_TYPE"] = DATASOURCE_TYPE
    loc_map["CAN_PORT"] = str(settings.can_port)
    loc_map["CAN_HOST"] = settings.can_host
    loc_map["DISTANCE_MAX"] = str(DISTANCE_MAX)
    loc_map["HASH"] = get_hash()

    def map_data(data):
        for k in loc_map:
            data = data.replace(k, loc_map[k])
        return data
    apply_dashboard(loc_template_path, map_data)

def apply_general():
    general_template_path = os.path.join(VIEWS_DIR, "general.json.template")
    general_map = dict()
    general_map["LOG_LIMIT"] = str(LOG_LIMIT)
    general_map["DATASOURCE_UID"] = DATASOURCE_UID
    general_map["DATASOURCE_TYPE"] = DATASOURCE_TYPE
    general_map["CAN_PORT"] = str(settings.can_port)
    general_map["CAN_HOST"] = settings.can_host
    general_map["HASH"] = get_hash()

    def map_data(data):
        for k in general_map:
            data = data.replace(k, general_map[k])
        return data
    apply_dashboard(general_template_path, map_data)


def read_loc_usage(mfxuid):
    loc_filter = requote_uri(f'mfxuid eq {mfxuid}')
    url = f'http://{DATABASE_HOST}:{DATABASE_PORT}/getConfigUsageMessage?filter={loc_filter}&limit=1'
    usage_data = requests.get(url).json()
    print(usage_data)
    if usage_data["total"] == 0:
        return DEFAULT_FUELA_MAX, DEFAULT_FUELB_MAX, DEFAULT_SAND_MAX
    
    max_fuel_a = usage_data["items"][0].get("maxFuelA", None)
    max_fuel_b = usage_data["items"][0].get("maxFuelB", None)
    max_sand = usage_data["items"][0].get("maxSand", None)

    if max_fuel_a is None:
        max_fuel_a = DEFAULT_FUELA_MAX
    if max_fuel_b is None:
        max_fuel_b = DEFAULT_FUELB_MAX
    if max_sand is None:
        max_sand = DEFAULT_SAND_MAX

    return max_fuel_a, max_fuel_b, max_sand


def update():
    locs = get_locs()
    if locs is None:
        print("Got no locs, retrying")
        update()
        return
    for loc in locs:
        print(f"Applying dashboard for {loc['name']}")
        max_fuel_a, max_fuel_b, max_sand = read_loc_usage(int(loc["mfxuid"], 0))
        apply_loc(loc, max_fuel_a, max_fuel_b, max_sand)

def main():
    apply_config(PORT)
    start_grafana()
    # Let grafana initialize the server
    time.sleep(5)


    apply_datasource(os.path.join(VIEWS_DIR, "datasource.json.template"), DATASOURCE_UID)
    apply_general()

    CAN_HASH = get_hash()
    while True:
        update()
        time.sleep(GRAFANA_UPDATE_INTERVAL)


if __name__ == "__main__":
    main()
