import subprocess
import threading
import cv2
import numpy as np

class ThreadedCamera:
    def __init__(self, rtsp_url):
        self.rtsp_url = rtsp_url
        self.status = {"is_running": False, "error": None}
        self.n_frame = None
        self.lock = threading.Lock()
        self.pipe = None
        self.capture_thread = threading.Thread(target=self._capture_stream, daemon=True)
        self.capture_thread.start()

    def start_ffmpeg(self, src):
        command = [
            'nice', '-n', '10',    # Lower priority
            'ffmpeg',
            '-i', src,
            '-vf', 'scale=960:540',
            '-f', 'rawvideo',
            '-pix_fmt', 'bgr24',
            '-an',
            '-sn',
            '-'
        ]
        self.pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

    def _capture_stream(self):
        try:
            self.start_ffmpeg(self.rtsp_url)

            with self.lock:
                self.status["is_running"] = True
                self.status["error"] = None

            while True:
                raw_frame = self.pipe.stdout.read(960 * 540 * 3)
                if not raw_frame:
                    with self.lock:
                        self.status["is_running"] = False
                        self.status["error"] = "Stream lost"
                    break

                frame = np.frombuffer(raw_frame, np.uint8).reshape((540, 960, 3))
                self.n_frame = frame

        except Exception as e:
            with self.lock:
                self.status["is_running"] = False
                self.status["error"] = str(e)
        finally:
            if self.pipe:
                self.pipe.terminate()
                self.pipe.wait()

    def get_status(self):
        with self.lock:
            return self.status

    def get_frame(self):
        with self.lock:
            return self.n_frame.copy() if self.n_frame is not None else None
    
