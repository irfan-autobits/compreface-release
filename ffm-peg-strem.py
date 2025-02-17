import os
import time
import cv2
import numpy as np
import subprocess
from threading import Thread

os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display

class ThreadedCamera(object):
    def __init__(self, src='rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live'):
        self.src = src
        self.pipe = None
        self.frames = None
        
        # Start FFmpeg process to read the RTSP stream
        self.start_ffmpeg()
        
        # Start FFplay for audio
        # self.start_audio()
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def start_ffmpeg(self):
        command = [
            'ffmpeg',
            # "-hwaccel", "cuda",                 # Enable CUDA hardware acceleration
            '-i', self.src,
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-sn',
            '-tune', 'zerolatency',
            '-'
        ]
        try:
            self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)
            time.sleep(1)  # give it a moment to start
            if self.pipe.poll() is not None:
                err = self.pipe.stderr.read().decode()
                print("FFmpeg process terminated immediately:", err)            
        except Exception as e:
            print(f"Error starting FFmpeg: {e}")


    def start_audio(self):
        # Start ffplay to play only the audio part of the RTSP stream
        audio_command = [
            'ffplay', '-nodisp', '-i', self.src, '-vn'
        ]
        self.audio_process = subprocess.Popen(audio_command)

    def update(self):
        while True:
            raw_frame = self.pipe.stdout.read(1920 * 1080 * 3)
            print("Read", len(raw_frame), "bytes")  # diagnostic print
            if len(raw_frame) != 1920 * 1080 * 3:
                err = self.pipe.stderr.read().decode()
                print("Failed to grab frame from FFmpeg. Expected", 1920 * 1080 * 3, "bytes, got", len(raw_frame))
                print("FFmpeg stderr:", err)
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((1080, 1920, 3))

    def show_frame(self):
        if self.frames is not None:
            cv2.imshow('RTSP Stream Test', self.frames)
            cv2.waitKey(1)
        else:
            print("No frame to display")

if __name__ == '__main__':
    src = 'rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live'
    try:
        threaded_camera = ThreadedCamera(src)
        while True:
            threaded_camera.show_frame()
    except Exception as e:
        print(f"Error: {e}")
