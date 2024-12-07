import shutil
import cv2
from compreface import CompreFace
from compreface.service import RecognitionService
import numpy as np
from dotenv import load_dotenv
import os

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

        compre_face: CompreFace = CompreFace(host, port, {
            "det_prob_threshold": FACE_DET_TH,
            "prediction_count": 1,
            "status": False
        })
        self.recognition: RecognitionService = compre_face.init_face_recognition(api_key)

    def write_frame(self, frame, frame_count):

        # Convert frame to bytes
        _, im_buf_arr = cv2.imencode(".jpg", frame)
        byte_frame = im_buf_arr.tobytes()

        # Send frame for recognition
        response = self.recognition.recognize(byte_frame)  

        try:
            # Attempt to get the detection result
            result = self.detect_face(frame)
        except Exception as e:
            # Handle any errors during face detection
            print(f"Error during face detection: {e}")
            result = None 

        if response:
            print(f'Responce_is_{response}')     
            if isinstance(result, dict) and 'box' in result:
                for result in response:
                    box = result.get('box')
                    subjects = result.get('subjects')
                    print('---got result------------------')
                    if box:
                        if subjects and subjects[0]['similarity'] >= self.FACE_REC_TH:
                            subjects = sorted(subjects, key=lambda k: k['similarity'], reverse=True)
                            subject = f"{subjects[0]['subject']}"
                            similarity = f"Similarity: {subjects[0]['similarity']}"
                            cv2.rectangle(img=frame, pt1=(box['x_min'], box['y_min']),
                                    pt2=(box['x_max'], box['y_max']), color=(0, 255, 0), thickness=1)
                            cv2.putText(frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                            
                            face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
                            image_name = f"{similarity}_{subject}_{frame_count}_.jpg"
                            image_path = os.path.join(frame_dir, image_name)
                            print(f'saved at {image_path}')
                            cv2.imwrite(image_path, face_image)
                        else:
                            subject = f"UNknown"
                            cv2.rectangle(img=frame, pt1=(box['x_min'], box['y_min']),
                                    pt2=(box['x_max'], box['y_max']), color=(0, 0, 255), thickness=1)
                            cv2.putText(frame, subject, (box['x_min']+5, box['y_min'] - 15),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 1)
                            
                            face_image = self.frame[box['y_min']:box['y_max'], box['x_min']:box['x_max']]
                            image_name = f"{similarity}_{subject}_{frame_count}_.jpg"
                            image_path = os.path.join(frame_dir, image_name)
                            print(f'saved at {image_path}')
                            cv2.imwrite(image_path, face_image)       

            # image_name = f'f_{frame_count}.jpg'
            # image_path = os.path.join(frame_dir, image_name)
            # cv2.imwrite(image_path, frame)
