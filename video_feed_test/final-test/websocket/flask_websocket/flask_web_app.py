from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import cv2
import base64
import io
from threading import Lock
from VideoCapture import VideoStream  # Assuming you have the class defined in VideoStream.py

app = Flask(__name__)
socketio = SocketIO(app)

# Global lock for ensuring thread-safe frame access
frame_lock = Lock()

# Initialize the VideoStream
vs = VideoStream(src='rtsp://autobits:Autobits@1234@192.168.1.202:554')  # Replace with your RTSP link or webcam index
vs.start()

def send_frame():
    FPS= 1/30  # 30 FPS
    """Thread function to send frames to the client"""
    while True:
        # Get the latest frame
        frame = vs.read()
        if frame is not None:
            # Encode the frame as JPEG
            _, buffer = cv2.imencode('.jpg', frame)
            frame_data = base64.b64encode(buffer).decode('utf-8')
            # Emit the frame to the client via WebSocket
            print("Emitting frame---------------------------------------")
            socketio.emit('frame', {'image': frame_data})
        else:
            print("Frame is None")
        socketio.sleep(FPS)  

@app.route('/')
def index():
    """Render the video feed page"""
    return render_template('index_lock.html')

# Start a thread to send frames to the client
socketio.start_background_task(send_frame)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
