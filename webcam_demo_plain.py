import os
os.environ['QT_QPA_PLATFORM'] = 'xcb'  # Or 'offscreen' if you want no display
import cv2
import argparse
import time
import shutil
import numpy as np
from threading import Thread
import pandas as pd
from compreface import CompreFace
from compreface.service import RecognitionService
from datetime import datetime
import struct
# Generate the timestamp
timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
# Directory to store employee images
database_dir = 'Report'
# Create the main database directory if it doesn't exist
shutil.rmtree(database_dir, ignore_errors=True)
os.makedirs(database_dir, exist_ok=True)
print('created/checked database_dir')
excel_name = 'face_recognition_results.xlsx'
excel_path = os.path.join(database_dir, excel_name)
txt_name = 'face_recognition_results.txt'
acc_file_path = os.path.join(database_dir, txt_name)

def parseArguments():
    parser = argparse.ArgumentParser()

    parser.add_argument("--api-key", help="CompreFace recognition service API key", type=str, default='88910b39-ac74-4fea-afcd-cfc446de2e6e')
    parser.add_argument("--host", help="CompreFace host", type=str, default='http://localhost')
    parser.add_argument("--port", help="CompreFace port", type=str, default='8000')
    parser.add_argument("--rtsp", help="Use RTSP stream (True/False)", type=str, default='True')
    parser.add_argument("--rtsp-url", help="RTSP stream URL", type=str, default='rtsp://autobits:Autobits@123@192.168.1.204:554')

    args = parser.parse_args()
    args.rtsp = args.rtsp.lower() == 'true'
    return args

class ThreadedCamera:
    def __init__(self, api_key, host, port, use_rtsp, rtsp_url):
        self.active = True
        self.results = []
        if use_rtsp:
            self.capture = cv2.VideoCapture(rtsp_url)
            self.get_stream_info(self.capture, "RTSP")
        else:
            self.capture = cv2.VideoCapture(0)
            self.get_stream_info(self.capture, "Internal Camera")

        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 2)
        # self.capture.set(cv2.CAP_PROP_FPS, 30)  # Limit to 15 FPS


        compre_face: CompreFace = CompreFace(host, port, {
                                                "limit": 0,
                                                "det_prob_threshold": 0.8,
                                                "prediction_count": 1,
                                                # "face_plugins": "",
                                                "status": False
                                            })

        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        self.FPS = 1/25
        self.FPS_MS = int(self.FPS * 1000)

        # Start frame retrieval thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()

    def show_frame(self):
        print("Started")
        while self.capture.isOpened():
            start_time = time.time()
            (status, frame_raw) = self.capture.read()
            
            # Check if a valid frame was received
            if not status or frame_raw is None or frame_raw.size == 0:
                print("No frame received, skipping...")
                time.sleep(self.FPS)  # Prevent tight loop if no frames are coming in
                continue  # Skip the rest of the loop if no frame
            # self.frame = cv2.flip(frame_raw, 1)
            # print(f"Frame status: {status}, Frame size: {frame_raw.size if frame_raw is not None else 'None'}")
            self.frame = frame_raw
            if self.results:
                results = self.results
                for result in results:
                    box = result.get('box')
                    subjects = result.get('subjects')
                    if box:
                        if subjects and subjects[0]['similarity'] >= 0.97:
                            
                            subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                            subject = f"{subjects[0]['subject']}"
                            similarity = f"Similarity: {subjects[0]['similarity']}"
                            cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                      pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
                            cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            
                            # # saving img
                            # # Extract face region using bounding box
                            # face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
                            # # Define file path to save the image
                            # face_image_name = f"{timestamp}_{subjects[0]['subject']}_({subjects[0]['similarity']})_{frame_count}.jpg"
                            # face_image_path = os.path.join(database_dir, face_image_name)
                            # # Save the face as a JPG image
                            # # cv2.imwrite(face_image_path, face_image)
                            # print(f"Saved detected at if face as: {face_image_name}")

                        else:
                            subject = f"Unknown"
                            cv2.rectangle(img=self.frame, pt1=(box['x_min'], box['y_min']),
                                      pt2=(box['x_max'], box['y_max']), color=(0, 0, 255), thickness=1)
                            cv2.putText(self.frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)

                            # # saving img
                            # # Extract face region using bounding box
                            # face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
                            # # Define file path to save the image
                            # face_image_name = f"{timestamp}_{frame_count}.jpg"
                            # face_image_path = os.path.join(database_dir, face_image_name)
                            # # Save the face as a JPG image
                            # # cv2.imwrite(face_image_path, face_image)
                            # print(f"Saved detected face as: {face_image_name}")

            # cv2.imshow('CompreFace demo', self.frame)
            time.sleep(self.FPS)
            # cv2.waitKey(self.FPS_MS)

            # if cv2.waitKey(1) & 0xFF == 27 or 0xFF == ord('q'):
            #     self.capture.release()
            #     cv2.destroyAllWindows()
            #     self.active = False

    def is_active(self):
        return self.active

    def update(self,frame_count):
        if not hasattr(self, 'frame'):
            return

        _, im_buf_arr = cv2.imencode(".jpg", self.frame)
        byte_im = im_buf_arr.tobytes()
        data = self.recognition.recognize(byte_im)
        self.results = data.get('result')
        if self.results:
            results = self.results
            for result in results:
                box = result.get('box')
                subjects = result.get('subjects')
                if box:
                    if subjects and subjects[0]['similarity'] >= 0.97:
                        subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                        subject = f"Subject: {subjects[0]['subject']}"
                        similarity = f"Similarity: {subjects[0]['similarity']}"
                        face_image_name = f"{timestamp}_{subjects[0]['subject']}_({subjects[0]['similarity']})_{frame_count}.jpg"
                        with open(acc_file_path, 'a') as file:
                                file.write(f'Saved detected face as: {face_image_name}'+ '\n')
                        # print(f"Saved detected at if face as: {face_image_name}")
                    else:
                        subject = f"No known faces"
                        face_image_name = f"{timestamp}_{frame_count}.jpg"
                        with open(acc_file_path, 'a') as file:
                                file.write(f'Saved detected face as: {face_image_name}'+ '\n')
                        # print(f"Saved detected face as: {face_image_name}")  

        cv2.imshow('CompreFace demo', self.frame)
        cv2.waitKey(self.FPS_MS)

        if cv2.waitKey(1) & 0xFF == 27 or 0xFF == ord('q'):
            self.capture.release()
            cv2.destroyAllWindows()
            self.active = False

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
        print(f"Frame rate: {fps} FPS")
        print(f"Codec: {codec_str}")
        print("------------------------------")


        
if __name__ == '__main__':
    args = parseArguments()
    threaded_camera = ThreadedCamera(args.api_key, args.host, args.port, args.rtsp, args.rtsp_url)
    frame_interval = 1  # Process every 3rd frame
    frame_count = 0 
    try:
        while threaded_camera.is_active():
            frame_count += 1  # Increment frame counter
            # Skip frames that are not the 3rd one in sequence
            if frame_count % frame_interval != 0:
                # print(f'Skip-processing {frame_count},{frame_interval}')
                continue  # Skip this iteration and go to the next frame
            threaded_camera.update(frame_count)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        threaded_camera.capture.release()
        cv2.destroyAllWindows()