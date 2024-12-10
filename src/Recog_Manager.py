# CompreFace/Custom-dashboard/src/Recog_Manager.py
import json
import cv2
from compreface import CompreFace

class RecognitionManager:
    def __init__(self, api_key, face_det_th=0.8, face_rec_th=0.0):
        self.face_det_th = face_det_th
        self.face_rec_th = face_rec_th
        self.api_key = api_key
        self.compre_face = CompreFace('http://localhost', "8000", {
            "limit": 0,
            "det_prob_threshold": self.face_det_th,
            "prediction_count": 1,
            "status": False
        })
        self.recognition = self.compre_face.init_face_recognition(self.api_key)
        
    def recognize_face(self, frame):
        _, im_buf_arr = cv2.imencode(".jpg", frame)
        byte_im = im_buf_arr.tobytes()
        
        try:
            data = self.recognition.recognize(byte_im)
            return data.get('result', [])
        except json.JSONDecodeError:
            print("Error during recognition.")
            return []
        
        