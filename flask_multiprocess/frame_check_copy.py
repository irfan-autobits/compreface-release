# flask_multiprocess/frame_check.py
import shutil
from threading import Thread
import cv2
from compreface import CompreFace
from compreface.service import RecognitionService
import numpy as np
from dotenv import load_dotenv
import os
import time
import logging
logging.basicConfig(level=logging.INFO)

frame_dir = "frames"
shutil.rmtree(frame_dir, ignore_errors=True)
os.makedirs(frame_dir, exist_ok=True)

class FrameCheck:
    def __init__(self, api_key, host, port, FACE_REC_TH, FACE_DET_TH):
        self.api_key = api_key
        self.host = host
        self.port = port
        self.FACE_REC_TH = FACE_REC_TH
        self.FACE_DET_TH = FACE_DET_TH
        self.results = []
        self.frame_count = 0

        compre_face: CompreFace = CompreFace(host, port, {
            "det_prob_threshold": FACE_DET_TH,
            "prediction_count": 1,
            "status": False
        })
        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

        self.FPS = 1/30

        # Start frame retrieval thread
        self.thread = Thread(target=self.show_frame, args=())
        self.thread.daemon = True
        self.thread.start()
    def write_frame(self, frame, frame_count):
        self.frame_count = frame_count
        # Convert frame to bytes
        _, im_buf_arr = cv2.imencode(".jpg", frame)
        byte_frame = im_buf_arr.tobytes()

        # Measure API request time
        start_time = time.time()
        # response = self.recognition.recognize(byte_frame)
        # self.results = response.get('result')
        api_time = time.time() - start_time
        logging.info(f"API response time: {api_time} seconds")


    def show_frame(self):
        print("Started")
        # # Ensure the frame is writable
        frame = frame.copy()

        try:
            if self.results:
                print(f'Response is: {self.results}')
                for result in self.results:
                    box = result.get('box')
                    subjects = result.get('subjects')

                    if box:
                        # Draw bounding box
                        if subjects and subjects[0]['similarity'] >= self.FACE_REC_TH:
                            # Known face
                            subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                            subject = f"{subjects[0]['subject']}"
                            similarity = f"Similarity: {subjects[0]['similarity']}"
                            color = (0, 255, 0)  # Green for known faces
                        else:
                            # Unknown face
                            subject = "Unknown"
                            similarity = ""
                            color = (0, 0, 255)  # Red for unknown faces

                        # Draw the bounding box and label
                        cv2.rectangle(frame, 
                                    (box['x_min'], box['y_min']), 
                                    (box['x_max'], box['y_max']), 
                                    color, 2)
                        cv2.putText(frame, f"{subject} {similarity}", 
                                    (box['x_min'], box['y_min'] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                        # Save the cropped face
                        face_image = frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
                        image_name = f"{subject}_{self.frame_count}.jpg"
                        image_path = os.path.join(frame_dir, image_name)
                        cv2.imwrite(image_path, frame)
                        print(f"Saved face image at: {image_path}")
                        return frame
                    else:
                        print("No bounding box found in result.")
                        image_name = f"_{self.frame_count}.jpg"
                        image_path = os.path.join(frame_dir, image_name)
                        cv2.imwrite(image_path, frame)
                        return frame

            else:
                print(f"No face detected or invalid response: ")
                image_name = f"_{self.frame_count}.jpg"
                image_path = os.path.join(frame_dir, image_name)
                cv2.imwrite(image_path, frame)                
                return frame

        except Exception as e:
            print(f"Error during processing frame: {e}")
            return frame


        # Optionally save the whole frame
        # frame_path = os.path.join(frame_dir, f"frame_{frame_count:04d}.jpg")
        # cv2.imwrite(frame_path, frame)
        # cv2.imshow('Frame', frame)

            # image_name = f'f_{frame_count}.jpg'
            # image_path = os.path.join(frame_dir, image_name)
            # cv2.imwrite(image_path, frame)
