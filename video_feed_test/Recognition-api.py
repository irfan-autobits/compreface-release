# video_feed_test/Recognition-api.py
import argparse
import os
import cv2
import numpy as np
import subprocess
from threading import Thread

import cv2
import socket
import struct
import pickle


os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

class ThreadedCamera(object):
    def __init__(self, src, server_address, camera_id):
        self.src = src
        self.pipe = None
        self.frames = None
        self.server_address = server_address
        self.camera_id = camera_id
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
        # Connect to the central server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(server_address)
        self.client_socket.send(camera_id.encode('utf-8'))  # Send camera ID

        while True:
            raw_frame = self.pipe.stdout.read(frame_size)  # Assuming 1920x1080 resolution
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))
            # Serialize the frame and send to the server
            # data = pickle.dumps(self.frames)
            # size = struct.pack(">L", len(data))
            # self.client_socket.sendall(size + data)
            # time.sleep(0.1)  # Simulate frame rate                     

    def show_frame(self):
        if self.frames is not None:
            data = pickle.dumps(self.frames)
            size = struct.pack(">L", len(data))
            self.client_socket.sendall(size + data)

            # cv2.imshow('RTSP Stream Test', self.frames)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                print("Exiting...")
                self.active = False
                cv2.destroyAllWindows()            
                self.client_socket.close()            

        else:
            print("No frame to display")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtsp-url", type=str, default='0')
    parser.add_argument("--data-dir", type=str, default='Report')
    parser.add_argument("--cam-id", type=str, default='0')
    args = parser.parse_args()
    server_address = ("127.0.0.1", 8000)
    camera_id = args.cam_id # Unique camera ID
    frame_count = 0
    try:
        threaded_camera = ThreadedCamera(args.rtsp_url, server_address, camera_id)
        while True:
            if frame_count % 25 == 0:
                threaded_camera.show_frame()
            frame_count+=1
    except Exception as e:
        print(f"Error: {e}")
