import subprocess
import cv2
from threading import Thread, Lock

import numpy as np


class VideoStream(object):
    def __init__(self, src=0):
        """_Initializes the class instance with the video source. 
        By default, the source is set to 0, which means the default camera (usually the built-in webcam)._

        Args:
            src (str, optional): _camera source link_. Defaults to 0.
        """
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        self.started = False
        self.read_lock = Lock()

    def start(self):
        """_Starts a thread that continuously reads frames from the video source and updates the frame buffer. 
        The update method is called by this thread._

        Returns:
            _object_: _description_
        """
        if self.started:
            print("already started!!")
            return None
        self.started = True
        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        return self

    def update(self):
        """_Continuously reads frames from the video source and updates the frame buffer. 
        This method is called by the thread started by the start method._
        """
        while self.started:
            (grabbed, frame) = self.stream.read()
            self.read_lock.acquire()
            self.grabbed, self.frame = grabbed, frame
            self.read_lock.release()

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
            raw_frame = self.pipe.stdout.read(frame_size)  # Assuming 1920x1080 resolution
            if len(raw_frame) != frame_size:
                print("Failed to grab frame from FFmpeg")
                break
            self.frames = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))
            
    def read(self):
        """_Returns the latest frame from the frame buffer._

        Returns:
            _type_: _description_
        """
        self.read_lock.acquire()
        frame = self.frame
        self.read_lock.release()
        return frame

    def stop(self):
        """_Stops the thread that is reading frames from the video source._
        """
        self.started = False
        self.thread.join()

    def exit(self):
        """_Releases the video source._
        """
        self.stream.release()