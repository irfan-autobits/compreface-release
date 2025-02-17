# bash-multiprocess/bash-multiprocess.py
from datetime import datetime
import json
import subprocess
import sys
import cv2
from flask import Flask, Response, jsonify
from multiprocessing import Manager, Process
import os
import time
import socket
import threading
import struct
import pickle

from multiprocessing import Queue
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)
CAMERA_SOURCES = os.getenv("CAMERA_SOURCES", "{}")
frames = {}  # Store frames for each camera

# Shared dictionary to store camera statuses
manager = Manager()
status_dict = manager.dict()

# Function to simulate running a camera process
def run_camera_sub(camera_id, rtsp_url, database_dir, status_dict):
    try:
        # Update status to running
        status_dict[camera_id] = {"status": "running", "pid": os.getpid(), "error": None}
        print(f"Camera {camera_id} started with PID {os.getpid()}")

        # Using subprocess.Popen to call the camera recognition script
        process = subprocess.Popen(["python3", "Recognition-api.py", 
                                    "--rtsp-url", rtsp_url 
                                    ])
        process.wait()
    except Exception as e:
        # Update status to failed on exception
        status_dict[camera_id] = {"status": "failed", "pid": None, "error": str(e)}
        print(f"Camera {camera_id} failed with error: {e}")

# Function to simulate running a camera process
def run_camera(camera_id, rtsp_url, database_dir, status_dict):
    try:
        # Update status to running
        status_dict[camera_id] = {"status": "running", "pid": os.getpid(), "error": None}
        print(f"Camera {camera_id} started with PID {os.getpid()}")
        # Simulate camera process or run actual ffmpeg script
        os.system(f"python3 Recognition-api.py --rtsp-url {rtsp_url} --data-dir {database_dir} --cam-id {camera_id}")
    
    except Exception as e:
        # Update status to failed on exception
        status_dict[camera_id] = {"status": "failed", "pid": None, "error": str(e)}
        print(f"Camera {camera_id} failed with error: {e}")

# Flask route to fetch camera statuses
@app.route("/status", methods=["GET"])
def get_status():
    # Convert status_dict to a regular dict for JSON serialization
    return jsonify({cam_id: data for cam_id, data in status_dict.items()})

def handle_camera_connection(conn, addr, camera_id):
    global frames
    try:
        while True:
            # Receive frame size
            packed_size = conn.recv(4)
            if not packed_size:
                print(f"Connection closed for camera {camera_id}")
                break
            size = struct.unpack(">L", packed_size)[0]

            # Receive frame data
            data = b""
            while len(data) < size:
                packet = conn.recv(size - len(data))
                if not packet:
                    print(f"Partial frame received for camera {camera_id}")
                    break
                data += packet

            # Deserialize and store the frame
            frame = pickle.loads(data)
            # if frame is not None:
            #     print(f"Received frame for camera {camera_id}, shape: {frame.shape}")
            # else:
            #     print(f"Invalid frame received for camera {camera_id}")
            frames[camera_id] = frame
    except Exception as e:
        print(f"Error in camera connection for {camera_id}: {e}")
    finally:
        conn.close()

@app.route('/camera/<camera_id>')
def stream(camera_id):
    def generate():
        print(f"Streaming for camera {camera_id}")
        while True:
            if camera_id in frames and frames[camera_id] is not None:
                frame = frames[camera_id]
                print(f"Sending frame for camera {camera_id}, shape: {frame.shape}")
                _, buffer = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            else:
                print(f"No valid frame for camera {camera_id}")
                # time.sleep(0.1)  # Avoid high CPU usage when no frames are available
    return Response(generate(), content_type='multipart/x-mixed-replace; boundary=frame')

def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Central server listening on {host}:{port}...")

    while True:
        conn, addr = server_socket.accept()
        # Receive camera ID from the client
        camera_id = conn.recv(1024).decode('utf-8').strip()  # Expect client to send ID on connect
        print(f"Camera connected: {camera_id}")
        threading.Thread(target=handle_camera_connection, args=(conn, addr, camera_id)).start()

if __name__ == "__main__":
    # Define camera configurations
    cameras = json.loads(CAMERA_SOURCES)
    active_cameras = [camera for camera in cameras if camera.get('enabled', True)]
    
    processes = []
    # Start camera processes
    for cam in active_cameras:
        process = Process(target=run_camera, args=(cam["id"], cam["rtsp_url"], cam["data_dir"], status_dict))
        process.start()
        processes.append(process)
   
    try:
        threading.Thread(target=start_server, args=("127.0.0.1", 8000), daemon=True).start()
        # process = Process(target=start_server, args=("127.0.0.1", 8000)).start()
        print("Starting Flask app...")
        app.run(host="0.0.0.0", port=5001, debug=False)
    except KeyboardInterrupt:
        print("Shutting down camera processes.........................")
        for process in processes:
            process.terminate()
            process.join()
