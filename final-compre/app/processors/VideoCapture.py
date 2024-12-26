# final-compre/app/processors/VideoCapture.py
import subprocess
import cv2
import numpy as np
from threading import Thread, Lock

class VideoStream(object):
    def __init__(self, src=0, width=960, height=540):
        """
        Initializes the VideoStream instance with FFmpeg as the backend.

        Args:
            src (str or int): Video source (e.g., RTSP link or webcam index).
            width (int): Width of the output frames.
            height (int): Height of the output frames.
        """
        self.src = src
        self.width = width
        self.height = height
        self.frame_size = width * height * 3
        self.started = False
        self.read_lock = Lock()
        self.frame = None
        self.pipe = None

    def start(self):
        """
        Starts the FFmpeg subprocess and spawns a thread to read frames.

        Returns:
            self: The VideoStream instance.
        """
        if self.started:
            print("Stream already started!")
            return None
        self.started = True
        self._start_ffmpeg()
        self.thread = Thread(target=self._update, args=())
        self.thread.daemon = True
        self.thread.start()
        return self

    def _start_ffmpeg(self):
        """
        Launches the FFmpeg process to decode the video source.
        """
        command = [
            "ffmpeg",
            "-i", self.src,                      # Input video source
            "-vf", f"scale={self.width}:{self.height}",  # Resize video
            "-f", "rawvideo",                    # Output raw video format
            "-pix_fmt", "bgr24",                 # OpenCV-compatible pixel format
            "-an",                               # Disable audio
            "-sn",                               # Disable subtitles
            "-tune", "zerolatency",              # Optimize for low latency
            "-"                                  # Output to stdout
        ]
        print(f"ffm-peg started for {self.src}")
        self.pipe = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8
        )

    def _update(self):
        """
        Continuously reads frames from FFmpeg's stdout and updates the frame buffer.
        """
        while self.started:
            raw_frame = self.pipe.stdout.read(self.frame_size)
            if len(raw_frame) != self.frame_size:
                print("Failed to grab frame or end of stream")
                self.started = False
                break
            frame = np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, 3))
            with self.read_lock:
                self.frame = frame

    def read(self):
        """
        Returns the latest frame from the buffer.

        Returns:
            np.ndarray or None: The latest frame, or None if no frame is available.
        """
        with self.read_lock:
            if self.frame is not None :
                return self.frame.copy() 
            else: 
                return None

    def stop(self):
        """
        Stops the frame-reading thread and cleans up FFmpeg resources.
        """
        if not self.started:
            return
        self.started = False
        if self.thread.is_alive():
            self.thread.join()        
        if self.pipe:
            self.pipe.terminate()
            self.pipe = None

    def __del__(self):
        """
        Ensures resources are cleaned up when the instance is deleted.
        """
        self.stop()
