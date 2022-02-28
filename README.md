# Maerklin CAN HTTP Service
A collection of micro services, scripts and demos revolving around the Märklin CS3+ CAN.

## Table of contents
- [Installation](#Installation)
- [Configuration](#Configuration)
- [Usage](#Usage)

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
# Now install via requirements.txt'
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

## Configuration
Ports, host addresses and other configs for the services (and some scripts) can be changed in the configuration file `config.py`.<br>
Values can temporarily be changed through the environment:
```sh
key=value python ./src/start.py starting_something_useful
# e.g. increasing the timeout for testing:
can_timeout=10000 python ./src/start.py can
```


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

# Shortcut for running raw_can_sender, raw_can_receiver, can_sender, can_receiver
You can use tmuxp profile for loading a preconfigured tmux session by running
```
tmuxp load ./assets/4-window-receive-and-send.tmuxp.yaml
```
Tmuxp will take care of activating the venv for you.

### Development
When no Märklin CS3+ is available, the `dummy_central_station.py` script may be used. It will forward all received CAN messages to the connected `raw_can_receiver` service.
```sh
python ./src/start.py dummy_central_station
```

## Documentation
Documentation for the various services can be found in the `./doc` folder:
- [Raw Can Receiver](./doc/raw_can_receiver.md)
- [Can Receiver](./doc/can_receiver.md)
- [High level CAN interface](./doc/high_level_can.md)
