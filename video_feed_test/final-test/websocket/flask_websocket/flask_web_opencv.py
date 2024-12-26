# video_feed_test/final-test/websocket/flask_websocket/flask_web_opencv.py
import logging
import cv2
import base64
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

# Flask App Setup
app = Flask(__name__)
socketio = SocketIO(app)  # Flask-SocketIO

# Route to serve HTML
@app.route('/')
def index():
    return render_template('index.html')

# WebSocket handler
@socketio.on('connect')
def video_feed():
    logging.info("Client connected")
    src = "rtsp://autobits:Autobits@123@192.168.1.204:554"
    FPS = 1 / 45  # ~45 FPS

    # Open the video capture instance
    cap = cv2.VideoCapture(0)
    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break              
            if frame is not None:
                # Encode frame as JPEG
                _, buffer = cv2.imencode('.jpg', frame)

                # Convert to base64
                frame_b64 = base64.b64encode(buffer).decode('utf-8')

                # Emit frame over WebSocket
                socketio.emit('video_frame', frame_b64)

                # Sleep to control frame rate
                time.sleep(FPS)
            else:
                logging.warning("Frame is None for camera")
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        cap.release()
# Run Flask app with SocketIO
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080)
