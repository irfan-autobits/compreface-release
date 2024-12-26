# final-compre/run.py
import json
from flask import Flask
from flask_socketio import SocketIO, emit
import cv2
import base64
from config.Paths import frame_lock, cam_sources, vs_list
from config.logger_config import cam_stat_logger , console_logger
from config.config import Config
from app.routes.Route import bp as video_feed_bp, active_cameras
from app.models.model import Detection, db, Camera_list
from scripts.manage_db import manage_table
from app.processors.face_detection import FaceDetectionProcessor
from app.services.camera_manager import Default_cameras
from flask_cors import CORS 

def create_app():
    app = Flask(__name__, template_folder='app/templates')  # Specify template folder
    app.config.from_object(Config)
    
    # Register blueprint
    app.register_blueprint(video_feed_bp, url_prefix='/')
    return app

app = create_app()

# Enable CORS for all routes, including SocketIO
# CORS(app, origins=["http://localhost:3000"])
CORS(app, resources={r"/*": {"origins": "*"}})  # Adjust the wildcard "*" to specific origins for better security.

# Initialize Flask-SocketIO
# socketio = SocketIO(app, cors_allowed_origins="http://localhost:3000")
socketio = SocketIO(app, cors_allowed_origins="*")
# socketio = SocketIO(app)

# Initialize the database
db.init_app(app)

# add default camera
with app.app_context():
    manage_table(drop = True) # drop all tables
    responce, status = Default_cameras()
print("default camera added",responce)

face_processor = FaceDetectionProcessor(cam_sources, db.session, app)

def send_frame():
    FPS = 1 / 45  # 30 FPS
    frame_count = 0
    """function to send frames to the client from all cameras"""
    try:
        with app.app_context():  # Explicitly create an app context
            while True:
                with frame_lock:  # Ensure thread-safe access
                    for cam_name, vs in list(vs_list.items()):  # Create a list to avoid runtime changes
                        frame = vs.read()
                        frame_count += 1
                        if frame is not None:
                            if frame_count % 30 == 0:
                                cam_stat_logger.info(f"Processed {frame_count} frames from camera {cam_name}")
                            frame = face_processor.process_frame(frame, cam_name)
                            # Encode the frame as JPEG
                            _, buffer = cv2.imencode('.jpg', frame)
                            frame_data = base64.b64encode(buffer).decode('utf-8')
                            # Emit the frame to the client via WebSocket
                            socketio.emit('frame', {'camera_name': cam_name, 'image': frame_data})
                        else:
                            if frame_count % 30 == 0:
                                cam_stat_logger.warning(f"No frame read from camera {cam_name} after {frame_count} attempts")
                            socketio.emit('frame', {'camera_name': cam_name})
                socketio.sleep(FPS)     
    except Exception as e:
        cam_stat_logger.error(f"Error in send_frame: {e}")
        socketio.emit('error', {'error': str(e)})

if __name__ == '__main__':
    with app.app_context():
        # Ensure the table exists before starting the application
        socketio.start_background_task(send_frame)  # Start the thread within app context
    socketio.run(app, host='0.0.0.0', port=5757, debug=False)
