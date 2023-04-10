# autopep8: off
# For correct threading and flask_socketio initialization
from eventlet import monkey_patch; monkey_patch()
# autopep8: on

import os

import socketio
from dotenv import load_dotenv
from flask import Flask, request
from flask_socketio import SocketIO

from src.ftp_loader import FtpLoader
from src.simulation import Simulation
from src.simulation_runner import SimulationRunner
from src.webnotifier import WebSocketNotifier
from src.log import logger


load_dotenv()


FTP_SERVER = os.getenv('FTP_SERVER')
FTP_USER = os.getenv('FTP_USER')
FTP_PASSWORD = os.getenv('FTP_PASSWORD')
SIMULATION_EXECUTABLE = os.getenv('SIMULATION_EXECUTABLE')

app = Flask(__name__)
ws = SocketIO(app, async_mode='eventlet')

notifier = WebSocketNotifier(ws)
ftp_loader = FtpLoader(FTP_SERVER, FTP_USER, FTP_PASSWORD)

runner = SimulationRunner(SIMULATION_EXECUTABLE, notifier)
simulation = Simulation(runner, ftp_loader, notifier)


@ws.event
def connect():
    logger.info(f'Create new connection from {request.remote_addr}')


@ws.event
def disconnect():
    logger.info(f'Client from {request.remote_addr} disconnected')


@app.post('/start')
def start_simulation():
    if simulation.is_running():
        return {'error': 'Attempt to start running simulation'}, 500

    xml_input = request.data
    simulation.run_model_xml(xml_input)
    return {'status': 'OK'}


@app.get('/stop')
def stop_simulation():
    logger.info('Stoppping simulation')
    try:
        simulation.stop()
        simulation.wait()
        return {'status': 'OK'}
    except Exception as err:
        return {'error': str(err)}, 500


if __name__ == '__main__':
    logger.info(f'Start running server on port 8000 ...')
    ws.run(app, port=8000)
    logger.info(f'Stop server ...')
