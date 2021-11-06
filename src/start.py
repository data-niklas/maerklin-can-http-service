from config import get_settings
import sys
import subprocess
import os
import signal

FILE_DIR = os.path.dirname(os.path.realpath(__file__))
SCRIPT_PREFIX = "./app/scripts/"
SCRIPT_POSTFIX = ".py"

ASGI_SERVICES = ["raw_can_receiver", "raw_can_sender", "can_receiver", "can_sender", "can"]
SCRIPTS = ["dummy_central_station", "websocket_logger", "websocket_printer"]

HELP = """A start script to run various ASGI routers and scripts, which work with the Märklin CAN interface.

Usage:
python start.py <router or script>

Routers:
"""+ ", ".join(ASGI_SERVICES) + """
Scripts:
"""+ ", ".join(SCRIPTS)


active_process = None

def supported_services():
    return ASGI_SERVICES + SCRIPTS

def print_help():
    print(HELP)
    sys.exit(0)

def run(command):
    global active_process
    print(f'\'{" ".join(command)}\'' )
    print()
    active_process = subprocess.Popen(command, stdout=sys.stdout, stderr=sys.stderr, cwd=FILE_DIR)
    active_process.wait()

def start_script(script):
    settings = get_settings()
    command = [settings.script_command, SCRIPT_PREFIX + script + SCRIPT_POSTFIX]
    run(command)

def start_wsgi(name):
    settings = get_settings()
    port = getattr(settings, name + '_port')
    host = getattr(settings, name + '_host')
    command = [settings.asgi_command, f'main:{name}', f'--port={port}', f'--host={host}', '--reload']
    run(command)

def start_service(service):
    if service in SCRIPTS:
        start_script(service)
    else:
        start_wsgi(service)

def signal_handler(sig, frame):
    global active_process
    if not active_process is None:
        active_process.kill()
    sys.exit(0)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not len(args) == 1:
        print(f'Invalid number of arguments {len(args)}. 1 expected.')
        print_help()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    service = args[0]
    if not service in supported_services():
        print(f'Invalid service {service}')
        print_help()

    start_service(service)
