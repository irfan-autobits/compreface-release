# final-compre/integrations/Compre_Api.py
import json
import cv2
from compreface import CompreFace
from config.Paths import HOST, PORT , API_KEY, FACE_DET_TH, FACE_DET_LM 

# Initialize CompreFace
compre_face = CompreFace(HOST, PORT, {
    "limit": int(FACE_DET_LM),                                                     # Limit the number of faces per frame
    "det_prob_threshold": float(FACE_DET_TH),                                      # Minimum detection probability threshold for face detection
    "prediction_count": 1,                                          # Number of estimate per face
    "face_plugins": "calculator,landmarks",         # "calculator = embedding,age,gender,landmarks,mask", 
    "status": False                                                  # execution_time and plugin_version fields
})

recognition = compre_face.init_face_recognition(API_KEY)
if recognition is None:
    print("Failed to initialize face recognition.")
    print(f"Host: {HOST}, Port: {PORT}, API Key: {API_KEY}")
else:
    print(f"CompreFace Started :: Host: {HOST}, Port: {PORT}, API Key: {API_KEY}")

def compreface_api(frame):

    # Example: Send frame to a recognition service
    _, im_buf_arr = cv2.imencode(".jpg", frame)
    byte_im = im_buf_arr.tobytes()
    try:
        data = recognition.recognize(byte_im)
        results = data.get('result')
    except json.JSONDecodeError:
        print("Failed to decode JSON response.")
        results = []

    return results