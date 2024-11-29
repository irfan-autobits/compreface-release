import json
import os
import sys
import cv2
import time
import argparse
import shutil
import numpy as np
import subprocess
from threading import Thread, Lock
from compreface import CompreFace
from datetime import datetime
import struct
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import re
from flask import Flask, Response
import threading

app = Flask(__name__)
lock = threading.Lock()

def generate_frames():
    while threaded_camera.active:
        with lock:
            if threaded_camera.frame is None:
                continue
            # Encode frame as JPEG
            _, buffer = cv2.imencode('.jpg', threaded_camera.frame)
            frame = buffer.tobytes()
        # Yield the frame in byte format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def start_flask():
    app.run(host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    host = 'http://localhost'
    port = '8000'
    api_key = API_KEY
    use_rtsp = args.rtsp_url != '0'

    camera_name = extract_ip_from_src(args.rtsp_url) if use_rtsp else 'Device_camera'
    camera_name = f"{camera_name}_{args.data_dir}"

    threaded_camera = ThreadedCamera(host, port, api_key, use_rtsp, camera_name, args.rtsp_url, args.data_dir)

    while threaded_camera.active:
        threaded_camera.show_frame()
