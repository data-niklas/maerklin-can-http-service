# Maerklin CAN HTTP Service
A collection of micro services, scripts and demos revolving around the Märklin CS3+ CAN.

## Table of contents
- [Installation](#Installation)
- [Configuration](#Configuration)
- [Usage](#Usage)


## Requirements
- [Python 3.8 or newer](https://www.python.org/downloads/)
- [Grafana](https://grafana.com/)
  - [Debian based Linux installation instructions](https://grafana.com/docs/grafana/next/setup-grafana/installation/debian/)
  - [RPM based Linux installation instructions](https://grafana.com/docs/grafana/next/setup-grafana/installation/rpm/)
- [tmux](https://github.com/tmux/tmux)
  - Does not work on Windows
  - Optional

## Installation
1. Clone the repository
```sh
git clone https://github.com/data-niklas/maerklin-can-http-service.git
# or
git clone git@github.com:data-niklas/maerklin-can-http-service.git
```
2. Create a Python virtual environment
```sh
cd maerklin-can-http-service
python -m venv venv
```
3. Install the requirements
```sh
# Activate the venv first!
## Linux:
source ./venv/bin/activate
## Windows
.\venv\Scripts\activate
# Now install further requirements via requirements.txt
pip install -r requirements.txt
```
4. Choose a Python ASGI server (preferably uvicorn)
```sh
# venv needs to be activated
pip install uvicorn
```

5. Setup the config
```sh
cd src
cp config.py.sample config.py
```

6. Change the default configuration according to your setup

## Configuration
Ports, host addresses and other configs for the services (and some scripts) can be changed in the configuration file `config.py`.<br>
Values can temporarily be changed through the environment:
```sh
key=value python ./src/start.py starting_something_useful
# e.g. increasing the timeout for testing:
can_timeout=10000 python ./src/start.py can
```

The `config.py` will be ignored by Git and can be modified freely. The config serves as a single point of truth and will be used by services to determine the `URI` of other services. Services might break if e.g.: the port of the `raw_can_receiver` is only temporarily changed for the `raw_can_receiver`, due to the difference between the declared port in the config and the actual port.


### Important values
1. `DEFAULT_GRAFANA_API_KEY`
- This value needs to be changed after installing the software!
- Open the Grafana web-ui
- Default credentials:
  - user: admin
  - password: admin
- Go to: `Settings -> API Key -> Create a new API key`
- API key needs role `Admin`
- Keep lifetime empty (the API key will not automatically invalidate and live indefinitely)
- Create new API key into `config.py`
- THE API KEY WILL NOT BE VISIBLE IN THE DASHBOARD AFTER YOU CONFIRMED THE CREATION OF THE API KEY
- Don't forget trailing `=`

2. `DEFAULT_CAN_TIMEOUT` (in milliseconds)
- The larger the value, the higher the response time of the services can be
- Large values catch slow responses from the CS3+, but increase the maximum latency
- In practice: A value like `5000` has proven effective (the CS3+ can be slow!)

3. `DEFAULT_RAW_CAN_IP`
- Set it to the IP-address of the CS3+

4. Service host config values
- Services will not work on the local network correctly by default
- Change all host configs of the services (not the `DEFAULT_RAW_CAN_IP`) to the IP of the computer in the local network (e.g.: `192.168.1.4`)


## Usage
> Don't forget the venv<br>

All services and the scripts in the `./src/app/scripts/` folder can be started through the `start.py` file.
```sh
# E.g. starting the raw sender and raw receiver.
python ./src/start.py raw_can_sender
python ./src/start.py raw_can_receiver
```
To list supported services and scripts, run `start.py` with no arguments.<br>

Services can be run directly through the ASGI server:
```sh
cd ./src
uvicorn main:raw_can_sender --reload
uvicorn main:raw_can_receiver --reload
```
Sending CAN messages can be tested through the generated Swagger API docs:
1. Start the sender service.
```sh
# Raw can sender, per default on http://127.0.0.1:8000
python ./src/start.py raw_can_sender
# or the can sender, per default on http://127.0.0.1:8002
python ./src/start.py can_sender
```
2. Navigate to the `/docs` subpage, e.g.: `http://127.0.0.1:8002/docs`
3. Choose a command and press `Try it out`

### Shortcut for running raw_can_sender, raw_can_receiver, can_sender, can_receiver
You can use tmuxp profile for loading a preconfigured tmux session by running
```
tmuxp load ./assets/4-window-receive-and-send.tmuxp.yaml
```
Tmuxp will take care of activating the venv for you.
Tmuxp can be closed via:
- ctrl+b 
- &
- y
- enter

### Shortcut to run most services and Grafana
You can use tmuxp profile for loading a preconfigured tmux session by running
```
tmuxp load ./assets/grafana.tmuxp.yaml
```
Tmuxp will take care of activating the venv for you.
Tmuxp can be closed via:
- ctrl+b 
- &
- y
- enter

- Grafana will not shutdown automatically on closing tmux, however Grafana will be killed on tmux start
- You can manually kill Grafana by running `sudo pkill grafana`

### Development
When no Märklin CS3+ is available, the `dummy_central_station.py` script may be used. It will forward all received CAN messages to the connected `raw_can_receiver` service.
```sh
python ./src/start.py dummy_central_station
```

## Documentation
Documentation for the various services can be found in the `./doc` folder:
- [Services](./doc/services.md)

## Troubleshooting
- Verify that the `venv` is active and all packages were installed inside of the `venv`
- Check if `config.py.sample` was updated. `config.py` might be outdated and changes from `config.py.sample` might need to be applied.
- Verify the configured IP's
