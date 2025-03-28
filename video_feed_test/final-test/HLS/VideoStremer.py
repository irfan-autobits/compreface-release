# video_feed_test/final-test/VideoStremer.py
import os
import subprocess
import cv2
import numpy as np
from threading import Thread, Lock

class VideoStream(object):
    def __init__(self, src=0, width=1920, height=1080):
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

    def _start_ffmpeg(self, output_dir="hls_output"):
        """
        Launches the FFmpeg process to decode the video source and generate HLS stream.
        Args:
            output_dir (str): Directory where HLS files will be stored.
        """
        os.makedirs(output_dir, exist_ok=True)
        command = [
            "ffmpeg",
            "-i", self.src,                        # Input video source
            "-vf", f"scale={self.width}:{self.height}",  # Resize video
            "-c:v", "libx264",                     # Encode video in H.264
            "-preset", "veryfast",                 # Low-latency encoding
            "-hls_time", "1",                      # Segment duration in seconds
            "-hls_list_size", "5",                 # Number of segments in playlist
            "-hls_flags", "delete_segments",       # Delete old segments
            f"{output_dir}/stream.m3u8"            # Output HLS stream
        ]
        self.pipe = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8
        )
        print(f"Started HLS stream for {self.src} at {output_dir}/stream.m3u8")


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
            return self.frame.copy() if self.frame is not None else None

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
