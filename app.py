# autopep8: off
# For correct threading and flask_socketio initialization
from eventlet import monkey_patch; monkey_patch()
# autopep8: on

from datetime import datetime
import os
import time
from threading import Lock, Thread

import socketio
from dotenv import load_dotenv
from flask import Flask, logging, request
from flask_socketio import SocketIO

from src.ftp_loader import FtpLoader
from src.simulation import Simulation
from src.simulation_runner import SimulationRunner
from src.webnotifier import WebSocketNotifier
from src.notifier import Status

import xmltodict
import tempfile

load_dotenv()


FTP_SERVER = os.getenv('FTP_SERVER')
FTP_USER = os.getenv('FTP_USER')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
SIMULATION_EXECUTABLE = os.getenv('SIMULATION_EXECUTABLE')

app = Flask(__name__)
ws = SocketIO(app, async_mode='eventlet')


notifier = WebSocketNotifier(ws)
ftp_loader = FtpLoader(FTP_SERVER, FTP_USER, FTP_PASSWORD)
ftp_loader.connect()


runner = SimulationRunner(SIMULATION_EXECUTABLE, notifier)
simulation = Simulation(runner, ftp_loader, notifier)


# TODO: move to another place
info = app.logger.info


@ws.event
def connect():
    info(f'Create new connection from {request.remote_addr}')


@ws.event
def disconnect():
    info(f'Client from {request.remote_addr} disconnected')


@app.post('/start')
async def start_simulation():
    xml_input = request.data
    xml = xmltodict.parse(xml_input)
    model_name = xml['model']['@name']

    info(f'Start new simulation "{model_name}" from {request.remote_addr}')
    workdir = tempfile.mkdtemp(
        prefix=model_name + '-', suffix='-{date:%Y-%m-%d_%H:%M:%S}'.format(date=datetime.now()))
    info(f'Create workdir {workdir}')

    config = os.path.join(workdir, 'model.xml')
    info(f'Write xml configuration to {config}')
    with open(config, 'wb') as config_file:
      config_file.write(xml_input)

    # TODO: make running of simulation asyncroous - no wait until simulation will end
    await simulation.run(workdir, config)
    return {'status': 'OK'}


@app.get('/stop')
def stop_simulation():
    pass

#     data = request.data
#     xml = xmltodict.parse(data)
#     model_name = xml['model']['@name']

#     # create directory for
#     experiment_directory = tempfile.mkdtemp(suffix='-suffix', prefix='prefix-')
#     app.logger.info(f'Create temp dir for experiment at {experiment_directory}')

#     # write xml to experiment directory


#     # start subprocess in experiment directory


#     #
#     #   - create subprocess
#     #   - translate stdout and stderr from subprocess
#     #   - notify about end
#     # zip directory and send it to ftp server

ws.run(app, port=8000)
