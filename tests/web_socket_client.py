import socketio


sio = socketio.Client()
url = 'http://localhost:8000'

@sio.event
def connect():
    print(f"Connected to {url}")

@sio.event
def connect_error(data):
    print(f"The connection failed! {data}")

@sio.event
def disconnect():
    print("Disconnected!")

@sio.event()
def message(data):
    print(f'Received msg {data}')

@sio.on('*')
def catch_all(event, data = ''):
    print(f'{event} - {data}')

sio.connect(url)
sio.wait()