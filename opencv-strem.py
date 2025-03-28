import struct
from threading import Thread
import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display
import cv2, time
import numpy as np

class ThreadedCamera(object):
    def __init__(self, src=0):
        self.capture = cv2.VideoCapture(src)
        # self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 0)
        self.get_stream_info(self.capture, "RTSP")
        self.new_width = 0
        self.new_height = 0
        # Ensure the video capture is successfully opened
        if not self.capture.isOpened():
            raise Exception(f"Failed to open video source: {src}")
        
        self.FPS = 1/25
        self.FPS_MS = int(self.FPS * 1000)
        
        # Start frame retrieval thread
        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        
    def update(self):
        while True:
            if self.capture.isOpened():
                self.status, self.frame = self.capture.read()
                if not self.status:
                    print("Failed to grab frame")
                    break  # Stop the loop if no frame is captured
    def prewhiten(self,img):
        """ Normalize image."""
        mean = np.mean(img)
        std = np.std(img)
        std_adj = np.maximum(std, 1.0 / np.sqrt(img.size))
        y = np.multiply(np.subtract(img, mean), 1 / std_adj)
        return y

    def show_frame(self):
        
        if self.frame is not None:
            # Resize the frame to 1080p resolution
            scale_factor = 2  # Modify as needed
            h, w = self.frame.shape[:2]
            self.new_width = w * scale_factor
            self.new_height = h * scale_factor
            self.frame = cv2.resize(self.frame, (self.new_width, self.new_height))
            cv2.imshow('frame', self.frame)
            cv2.waitKey(self.FPS_MS)
        else:
            print("No frame to display")

    def get_stream_info(self, capture, stream_type):
        if not capture.isOpened():
            print(f"Unable to open {stream_type} stream")
            return

        # Retrieve and print properties
        width = capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = capture.get(cv2.CAP_PROP_FRAME_HEIGHT)
        fps = capture.get(cv2.CAP_PROP_FPS)
        codec = capture.get(cv2.CAP_PROP_FOURCC)
        # Unpack the codec and decode it properly
        codec_bytes = struct.unpack('4s', struct.pack('<I', int(codec)))[0]
        codec_str = codec_bytes.decode('utf-8').strip()

        print(f"{stream_type} Stream Info:")
        print(f"Resolution: {int(width)} x {int(height)}")
        # print(f"New Res   : {int(self.new_width)} x {int(self.new_height)}")
        print(f"Frame rate: {fps} FPS")
        print(f"Codec: {codec_str}")
        print("------------------------------")

if __name__ == '__main__':
    src = 'rtsp://autobits:Autobits@123@192.168.1.204:554'
    # src1 = 'rtsp://autobits:Autobits@1234@192.168.1.202:554'
    src1 = 'rtsp://autobits:Autobits%401234@192.168.1.202:554'
    st = "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live"
    try:
        threaded_camera = ThreadedCamera()
        while True:
            try:
                threaded_camera.show_frame()
            except AttributeError:
                pass
    except Exception as e:
        print(f"Error: {e}")
