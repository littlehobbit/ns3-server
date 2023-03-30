import json
from flask_socketio import SocketIO
from src.notifier import Notifier, Status
# from app import app


class WebSocketNotifier(Notifier):

    def __init__(self, sio: SocketIO):
        self.sio = sio

    def send(self, status: Status, msg: str = ''):
        print(f'Send to clients status={status.name} msg={msg}')
        self.sio.send(
            json.dumps({
                'status': status.name,
                'msg': msg
            }), json=True)
