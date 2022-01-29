import sys
import os
import subprocess
import signal
import requests
import time
# Plugins needed: grafana-cli --pluginUrl https://github.com/cloudspout/cloudspout-button-panel/releases/download/7.0.23/cloudspout-button-panel.zip plugins install cloudspout-button-panel
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config import get_settings

settings = get_settings()

PORT = settings.grafana_port
HOMEFOLDER = settings.grafana_dir
API_KEY = settings.grafana_api_key
# Only works if a sqlite3 database was used and the path starts with an 'sqlite:///'
DATASOURCE_PATH = settings.high_level_db_dump_database[10:]


CONFIG_FILE = os.path.join(HOMEFOLDER, "conf", "defaults.ini")
CONFIG_TEMPLATE_FILE =  os.path.join(os.path.dirname(os.path.abspath(__file__)), "defaults.ini.template")
VIEWS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "views")
AUTHORIZATION_HEADER = {'Authorization': f'Bearer {API_KEY}'}

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

def apply_file(file, url, modifier_cb):
    with open(file, 'r', encoding="utf-8") as f:
        data = f.read()
        data = modifier_cb(data)
        result = requests.post(url, data=data, headers=AUTHORIZATION_HEADER)
        print(result.content)

def apply_datasource(file):
    apply_file(file, f'http://localhost:{PORT}/api/datasources', lambda data: data.replace("DBPATH", DATASOURCE_PATH))


def apply_dashboard(file):
    apply_file(file, f'http://localhost:{PORT}/api/dashboards/db', lambda data: """{
            "dashboard": """ + data +  """,
            "overwrite": true
    }""")

apply_config(PORT)
start_grafana()
time.sleep(2)

apply_datasource(os.path.join(VIEWS_DIR, "datasource.json"))
apply_dashboard(os.path.join(VIEWS_DIR, "general.json"))


# TODO implement applying views
import time
while True:
    time.sleep(10.0)