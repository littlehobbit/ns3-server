# ns3-server
Server for starting ns3 simulations from HTTP API. Uploads results to remote FTP storage.

## Installation
For installation clone this repo and run:
```bash
make init
```
This will install all dependencies. Now you can start server with `make run` command.

## Enviroment variables
| Variable              | Description                         |
|-----------------------|-------------------------------------|
| NS3_SERVER_PORT       | Port on with userver will run       |
| FTP_SERVER            | Address or remote artifacts server  |
| FTP_USER              | User for FTP                        |
| FTP_PASSWORD          | Password for FTP                    |
| SIMULATION_EXECUTABLE | Path to simulation-core executable  |


## API
| Path    | Type  | Content type    | Description                                 | Returns                                    |
|---------|-------|-----------------|---------------------------------------------|--------------------------------------------|
| /start  | POST  | application/xml | Start similation of model, provided in body | 200 if ok, 500 with error message overwise |
| /stop   | GET   | -               | Stops current running simulation            | 200 if ok, 500 with error message overwise |

## Usage
See scripts/send_model.sh for example