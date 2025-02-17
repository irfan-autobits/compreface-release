import socketio
import time

# import logging
# logging.basicConfig(level=logging.DEBUG)

# sio = socketio.Client(logger=True, engineio_logger=True)

sio = socketio.Client()

    
@sio.event
def connect():
    print("Connected to server")

@sio.event
def data(event):
    print("Received data:", event.get('2_min'))
    
@sio.event
def disconnect():
    print("Disconnected from server")

try:
    sio.connect('http://192.168.1.213:3001?token=yqjdHAvNM2y6kB2r2Lq7PLEXEtXTnPF6', transports='websocket')
    while True:
        time.sleep(1)
except Exception as e:
    print(f"Connection failed: {e}")
except KeyboardInterrupt:
    print("Exiting...")
finally:
    sio.disconnect()