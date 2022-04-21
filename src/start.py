from config import get_settings
import sys
import subprocess
import os
import signal
import time

settings = get_settings()

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_DIR = os.path.join(FILE_DIR, "app", "scripts")
EXTERNAL_SERVICE_DIR = os.path.join(FILE_DIR, "app", "external_services")
SCRIPT_POSTFIX = ".py"

ASGI_SERVICES = ["raw_can_receiver", "raw_can_sender", "can_receiver", "can_sender", "can", "database_read"]
EXTERNAL_SERVICES = ["grafana"]
SCRIPTS = ["dummy_central_station", "websocket_logger", "websocket_printer", "db_dump", \
    "raw_db_dump", "websocket_config_stream", "websocket_replay", "database_refresher", "database_resampler"]

WORKFLOW_TERMINAL_COMMAND = settings.workflow_terminal_command
WORKFLOW_INTERVAL = settings.workflow_terminal_interval

WORKFLOWS = dict()
WORKFLOWS["dummy_central_station"] = ["dummy_central_station", "raw_can_receiver", "can_receiver"]
WORKFLOWS["grafana"] = ["raw_can_receiver", "can_receiver", "db_dump", "grafana"]

HELP = """A start script to run various ASGI routers and scripts, which work with the Märklin CAN interface.

Usage:
python start.py <router or script>

 or

python start.py _ <workflow>

Routers:
"""+ ", ".join(ASGI_SERVICES) + """
External Services:
"""+ ", ".join(EXTERNAL_SERVICES) + """
Scripts:
"""+ ", ".join(SCRIPTS) + """
Workflows:
""" + ", ".join(WORKFLOWS.keys())


active_process = None

def supported_services():
    return ASGI_SERVICES + SCRIPTS + EXTERNAL_SERVICES

def print_help():
    print(HELP)
    sys.exit(0)

def run(command, spawn_new):
    global active_process
    if spawn_new:
        command = WORKFLOW_TERMINAL_COMMAND + command

    print(f'\'{" ".join(command)}\'' )
    print()
    active_process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, cwd=FILE_DIR)
    if not spawn_new:
        active_process.wait()

def start_script(script, spawn_new):
    global settings
    command = [settings.script_command, os.path.join(SCRIPT_DIR, script) + SCRIPT_POSTFIX]
    run(command, spawn_new)

def start_asgi(name, spawn_new):
    global settings
    port = getattr(settings, name + '_port')
    host = getattr(settings, name + '_host')
    command = [settings.asgi_command, f'main:{name}', f'--port={port}', f'--host={host}', '--reload']
    run(command, spawn_new)

def start_external(script, spawn_new):
    global settings
    command = [settings.script_command, os.path.join(EXTERNAL_SERVICE_DIR, script, "__init__") + SCRIPT_POSTFIX]
    run(command, spawn_new)



def start_service(service, spawn_new=False):
    if service in SCRIPTS:
        start_script(service, spawn_new)
    elif service in ASGI_SERVICES:
        start_asgi(service, spawn_new)
    else:
        start_external(service, spawn_new)

def start_workflow(workflow):
    for item in WORKFLOWS[workflow]:
        start_service(item, True)
        time.sleep(WORKFLOW_INTERVAL)

def signal_handler(sig, frame):
    global active_process
    if not active_process is None:
        active_process.kill()
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not len(args) == 1 and not len(args) == 2:
        print(f'Invalid number of arguments {len(args)}. 1-2 expected.')
        print_help()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    if len(args) == 2:
        workflow = args[1]
        if not workflow in WORKFLOWS:
            print(f'Invalid workflow {workflow}')
            print_help()
        start_workflow(workflow)
    else:
        service = args[0]
        if not service in supported_services():
            print(f'Invalid service {service}')
            print_help()

        start_service(service)
