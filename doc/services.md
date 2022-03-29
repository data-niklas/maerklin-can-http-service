# Services
This document provides a general overview over all microservices included in this repository. The services are split into three groups of services. The first group includes microservices which provide a service by exposing data of the Märklin CS3+ or writing data to it. They either expose their service through a HTTP or WebSocket interface. Those microservices will be referred to as `services` The second group includes microservices which don't provide such interface. They are referred to as `scripts` and provide general utility functionality. The last group includes `scripts` which bootstrap and control external services. Those will be referred to as `external services`. The microservices can be found in the `src > app > #` directory, where `#` is the name of the group of the microservice.


Each microservice can be started via `start.py` by passing the name of the microservice (without `.py`).<br>
Note: `venv` needs to be activated.


## Services
Each service is implemented as an `ASGI` router and included in the main file `main.py`. 

### raw_can_recv
[raw_can_recv directory](../src/app/services/raw_can_recv/)
#### Description
This microservice directly communicated with the CS3+ and exposes all received data through WebSockets. The received messages are parsed into objects of the `CANMessage` class (`src > app > schemas > can.py`) and then converted into JSON text so that the message can be passed to all connected WebSocket clients.

#### Configuration
- `HOST`: Host of the microservice
- `PORT`: Port of the microservice

#### Further Notes

### raw_can_send
[raw_can_send directory](../src/app/services/raw_can_send/)
#### Description
This microservice directly communicated with the CS3+ and writes all received data from WebSockets to the CS3+. The received JSON messages are parsed into objects of the [`CANMessage`](../src/app/schemas/can.py), converted into bytes and then sent to the CS3+.

#### Configuration
- `HOST`: Host of the microservice
- `PORT`: Port of the microservice

### high_level_can_recv
[high_level_can_recv directory](../src/app/services/high_level_can_recv/)
#### Description
This microservice serves as an extra abstraction layer above `raw_can_recv`. It provides high level objects for each CAN command. It connects to `raw_can_recv`, parses JSON messages into objects of the class corresponding to the command of the message, converts the object into JSON and then passes the new message to all connected clients. The classes of the corresponding CAN command can be found in [this directory](../src/app/schemas/can_commands/).

#### Configuration
- `HOST`: Host of the microservice
- `PORT`: Port of the microservice

#### Further Notes


## Scripts


## External Services