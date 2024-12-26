# final-compre/app/routes/Route.py
from flask import Blueprint, jsonify, render_template, request
from flask import current_app 
from app.services.user_management import sign_up_user, log_in_user
from app.services.camera_manager import Add_camera, Remove_camera, Start_camera, Stop_camera
from flask_socketio import SocketIO


# Blueprint for routes
bp = Blueprint('video_feed', __name__)

# Flag to control the camera feed
active_cameras = []

@bp.route('/')
def index():
    """Render the video feed page"""
    return {"nessage" : "accessed root page of flask."}, 200
    # return render_template('index_check.html')

@bp.route('/api/sign', methods=['POST'])
def sign():
    """API endpoint to save user data"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if email and password:
        responce, status = sign_up_user(email, password)
        return jsonify(responce), status
    else:
        return {"error": "Email and password are required"}, 400
    
@bp.route('/api/login', methods=['POST'])
def login():
    """API endpoint to save user data"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    return log_in_user(email, password)

@bp.route('/api/add_camera', methods=['POST'])
def add_camera():
    """API endpoint to add a camera"""
    data = request.get_json()
    camera_name = data.get('camera_name')
    camera_url = data.get('camera_url')
    if camera_name and camera_url:
        responce, status = Add_camera(camera_name,camera_url)
        return jsonify(responce), status
    else:
        return {'error' : 'Camera name or url not provided'}, 400

@bp.route('/api/remove_camera', methods=['POST'])
def remove_camera():
    """API endpoint to remove a camera"""
    data = request.get_json()
    camera_name = data.get('camera_name')
    camera_url = data.get('camera_url')
    if camera_name and camera_url:
        responce, status = Remove_camera(camera_name,camera_url)
        return jsonify(responce), status
    else:
        return {'error' : 'Camera name or url not provided'}, 400

@bp.route('/start_feed', methods=['POST'])
def start_feed():
    """Start the video feed"""
    data = request.get_json()
    camera_name = data.get('camera_name')
    if camera_name:
        # if camera_name in active_cameras:
        #     return {'message' : f'Video feed already started for {camera_name}'}, 200
        # else:
        #     active_cameras.append(camera_name)
        #     print(f"started :: {camera_name}")
        #     return {'message' : f'Video feed started for {camera_name}'} , 200
        responce, status = Start_camera(camera_name)
        return responce, status
    else:
        return {'error' : 'Camera name not provided for starting'}, 400

@bp.route('/stop_feed', methods=['POST'])
def stop_feed():
    """Stop the video feed"""
    data = request.get_json()
    camera_name = data.get('camera_name')
    if camera_name:
        # if camera_name in active_cameras:
        #     active_cameras.remove(camera_name)
        #     print(f"stopped :: {camera_name}")
        #     return {'message' : f'Video feed stopped for {camera_name}'} , 200
        # else:
        #     return {'message' : f'Video feed already stopped for {camera_name}'}, 200
        responce, status = Stop_camera(camera_name)
        return responce, status
    else:
        return {'error' : 'Camera name not provided for stopping'}, 400
    