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
        # Ensure the frame is writable
        frame = frame.copy()

        try:
            if response and 'result' in response:
                print(f'Response is: {response}')
                for result in response['result']:
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
                        image_name = f"{subject}_{frame_count}.jpg"
                        image_path = os.path.join(frame_dir, image_name)
                        cv2.imwrite(image_path, face_image)
                        print(f"Saved face image at: {image_path}")
                    else:
                        print("No bounding box found in result.")

            else:
                print(f"No face detected or invalid response: {response}")

        except Exception as e:
            print(f"Error during processing frame: {e}")

        # Optionally save the whole frame
        # frame_path = os.path.join(frame_dir, f"frame_{frame_count:04d}.jpg")
        # cv2.imwrite(frame_path, frame)
        # cv2.imshow('Frame', frame)

            # image_name = f'f_{frame_count}.jpg'
            # image_path = os.path.join(frame_dir, image_name)
            # cv2.imwrite(image_path, frame)
