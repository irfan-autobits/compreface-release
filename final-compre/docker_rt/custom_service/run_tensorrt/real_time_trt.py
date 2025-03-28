import cv2
import numpy as np
from custom_service.run_tensorrt.rt_inference import TensorRTInference
# from insightface.utils import face_align
from custom_service.run_tensorrt import face_align
# from insightface.app import FaceAnalysis
from config.Paths import INSIGHT_MODELS, model_pack_name, SECRET_KEY
from custom_service.output_formatter import formatter

det_model = INSIGHT_MODELS / model_pack_name / "det_10g.trt"
rec_model = INSIGHT_MODELS / model_pack_name / "w600k_r50.trt"

# initialization with TensorRT engines
detection_trt = TensorRTInference(str(det_model))
recognition_trt = TensorRTInference(str(rec_model))

def detect_faces(img):
    # Preprocessing
    input_img = cv2.resize(img, (640, 640))
    input_img = input_img.transpose(2, 0, 1)  # HWC to CHW
    input_img = np.expand_dims(input_img, axis=0).astype(np.float32)
    input_img = (input_img - 127.5) / 128.0  # InsightFace specific normalization
    
    # Inference
    outputs = detection_trt.infer(input_img)
    # Postprocessing (example for detection model)
    # You'll need to implement your model's specific postprocessing
    faces = []
    num_detections = outputs[0][0]
    print(f"face out {num_detections} :::: {outputs}")

    # for i in range(int(num_detections)):
    #     face = FaceAnalysis.Face(
    #         bbox=outputs[1][i*4:(i+1)*4],  # Adjust indices based on your model
    #         det_score=outputs[2][i],
    #         kps=outputs[3][i*10:(i+1)*10]  # Adjust for landmark output
    #     )
    #     faces.append(face)
    return faces

def recognize_faces_local(img, faces):
    for face in faces:
        # Crop and align face
        aimg = face_align.norm_crop(img, face.kps, 112)
        
        # Preprocessing
        input_img = aimg.transpose(2, 0, 1)  # HWC to CHW
        input_img = np.expand_dims(input_img, axis=0).astype(np.float32)
        input_img = (input_img - 127.5) / 128.0  # InsightFace normalization
        
        # Inference
        embedding = recognition_trt.infer(input_img)[0]
        
        # Postprocessing
        embedding /= np.linalg.norm(embedding)  # Normalize
        face.embedding = embedding
    
    return faces

def run_trtbuffalo(frame):
    # Detection
    detected_faces = detect_faces(frame)

    # Recognition
    # recognized_faces = recognize_faces_local(frame, detected_faces)
    compreface_results = []
    # For each detected face, store the embedding in the DB
    if detected_faces is not None:
        for face in detected_faces:
            # spoof_res = test(frame, face.bbox, str(spoof_dir), 0)
            spoof_res = [False, 0.0, 0.0]

            embedding = face.embedding  # Expected to be a numpy array
            if embedding is None:
                print("no embedding generated")
                continue
            # matches = verification(embedding)

            # Ensure matches exist before accessing
            # if not matches:
                print("No match found")
                continue  # Skip to the next face
            # print(f"faces {face}")
            # compreface_result = formatter(face, matches[0]["subject_name"], matches[0]["distance"], spoof_res, elapsed_time=0)
            compreface_result = formatter(face, "Unknown", "0", spoof_res, elapsed_time=0)
            compreface_results.append(compreface_result)

    # Rest of your existing processing...
    return compreface_results