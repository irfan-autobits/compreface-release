import argparse
import os
import cv2
import numpy as np
import subprocess
from threading import Thread
from flask import Flask, Response
import multiprocessing
import sys

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

app = Flask(__name__)

class ThreadedCamera(object):
    def __init__(self, src):
        self.src = src
        self.pipe = None
        self.frames = None
        
        # Start FFmpeg process to read the RTSP stream
        self.start_ffmpeg()
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_ffmpeg(self):
        command = [
            'ffmpeg',
            '-i', self.src,                     # Input RTSP stream
            '-vf', 'scale=960:540',
            '-f', 'rawvideo',                   # Output format
            '-pix_fmt', 'bgr24',                # Pixel format for OpenCV
            '-an',
            '-sn',                              # Disable subtitles
            '-tune', 'zerolatency',             # Tune for low latency
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=10**8)

    def update(self):
        frame_width = 960
        frame_height = 540
        frame_size = frame_width * frame_height * 3
        while True:
            raw_frame = self.pipe.stdout.read(frame_size)  # Assuming 960x540 resolution
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))

    def generate(self):
        """Generate MJPEG stream for Flask to send to the browser."""
        while True:
            if self.frames is not None:
                ret, jpeg = cv2.imencode('.jpg', self.frames)
                if ret:
                    frame = jpeg.tobytes()
                    yield (b'--frame\r\n'
                           b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                print("No frame to stream")

@app.route('/video_feed')
def video_feed():
    """Route to stream video."""
    return Response(threaded_camera.generate(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def run_rtsp_stream(rtsp_url):
    """Run the Recognition-api.py script for a given RTSP URL."""
    # Set the command for subprocess
    command = [
        sys.executable,  # Use the same Python interpreter
        'Recognition-api.py',
        '--rtsp-url', rtsp_url,
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"running RTSP stream {rtsp_url}")
    except subprocess.CalledProcessError as e:
        print(f"Error while running RTSP stream {rtsp_url}: {e}")

def start_multiple_streams(rtsp_urls):
    """Start multiple RTSP streams using multiprocessing."""
    with multiprocessing.Pool(processes=len(rtsp_urls)) as pool:
        pool.map(run_rtsp_stream, rtsp_urls)

if __name__ == '__main__':
    # Define a list of RTSP URLs
    rtsp_urls = [
        'rtsp://autobits:Autobits@123@192.168.1.204:554',
        'rtsp://autobits:Autobits@123@192.168.1.203:554',
    ]

    # Start the RTSP streams
    start_multiple_streams(rtsp_urls)
    
    # Start Flask server
    threaded_camera = ThreadedCamera(rtsp_urls[0])  # Assuming you want to start the first stream
    app.run(host='0.0.0.0', port=5001, threaded=True)
