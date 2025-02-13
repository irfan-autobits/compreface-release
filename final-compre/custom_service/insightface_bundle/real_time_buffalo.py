from insightface.app import FaceAnalysis
from insightface.model_zoo import get_model
import numpy as np
from custom_service.insightface_bundle.verify_euclidean_dis import verify_identity
from app.models.model import Raw_Embedding, db
from flask import current_app      

# Initialize the InsightFace app with detection and recognition modules.
# analy_app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
model_zoo = ['buffalo_l', 'buffalo_m', 'buffalo_s']
model_pack_name = model_zoo[1]
analy_app = FaceAnalysis(name=model_pack_name ,allowed_modules=['detection', 'landmark_3d_68'])
analy_app.prepare(ctx_id=0, det_size=(640, 640))

rec_handler = get_model('/home/irfan/.insightface/models/buffalo_m/w600k_r50.onnx')
rec_handler.prepare(ctx_id=0)

from custom_service.insightface_bundle.silent_antispoof.real_time_antispoof import test
from config.Paths import MODELS_DIR
spoof_dir = MODELS_DIR / "anti_spoof_models"

def verification(input_embedding):
    # Example usage with known embeddings from the database
    with current_app.app_context():
        embeddings = Raw_Embedding.query.all()
        
        # List of known embeddings from the database (you need to format this appropriately)
        known_embeddings = [{'subject_name': emb.subject_name, 'embedding': np.array(emb.embedding)} for emb in embeddings]
                
        # Get the top 3 closest matches
        matches = verify_identity(input_embedding, known_embeddings, top_n=1)
        return matches

def formatter(face, sub_nam, distance, spoof_res, elapsed_time=0):
    
    bbox = face.bbox
    landms = face.kps
    confidence = face.det_score
    age = face.age if hasattr(face, "age") else None
    gender = face.gender if hasattr(face, "gender") else None
    embedding = face.embedding.tolist() if getattr(face, "embedding", None) is not None else []
    landmark_3d_68 = face.landmark_3d_68 if getattr(face, "landmark_3d_68", None) is not None else []
    is_spoof = True if spoof_res[0] else False
    spoof_score = float(spoof_res[1]) if spoof_res[1] else 0.0
    spoof_dura = spoof_res[2] if spoof_res[2] else 0.0


    # Ensure bbox values are floats for precision
    x1, y1, x2, y2 = map(float, bbox[:4])  

    # Ensure landmarks exist before accessing
    if landms is not None and len(landms) >= 5:
        landmarks = {
            "left_eye": [float(landms[0][0]), float(landms[0][1])],
            "right_eye": [float(landms[1][0]), float(landms[1][1])],
            "nose": [float(landms[2][0]), float(landms[2][1])],
            "right_mouth": [float(landms[3][0]), float(landms[3][1])],
            "left_mouth": [float(landms[4][0]), float(landms[4][1])],
        }
    else:
        landmarks = {}

    # Format output in CompreFace format
    compreface_result = {
        "age": {
            "probability": None,  
            "high": None,
            "low": None,
            "value": age
        },
        "gender": {
            "probability": None,  
            "value": gender
        },
        "mask": {
            "probability": None,  
            "value": None
        },
        "embedding": embedding,  
        "box": {
            "probability": float(confidence),  
            "x_min": int(x1),
            "y_min": int(y1),
            "x_max": int(x2),
            "y_max": int(y2)
        },
        "landmarks": [
            landmarks.get("left_eye", []),
            landmarks.get("right_eye", []),
            landmarks.get("nose", []),
            landmarks.get("right_mouth", []),
            landmarks.get("left_mouth", [])
        ],
        "landmark_3d_68" : landmark_3d_68,
        "spoof_res": {
            "is_spoof" :is_spoof,
            "spoof_score":spoof_score,
            "spoof_dura":spoof_dura
        },
        "subjects": [
            { "subject": sub_nam, "similarity": distance }
        ],  
        "execution_time": {
            "age": None,
            "gender": None,
            "detector": elapsed_time,
            "calculator": None,
            "mask": None
        }
    }

    return compreface_result

# def run_buffalo(frame):
#     # Run face detection and recognition
#     faces = analy_app.get(frame)
#     compreface_results = []
#     is_spoof = False
#     # For each detected face, store the embedding in the DB
#     if faces is not None:
#         for face in faces:
#             spoof_res = test(frame, face.bbox, str(spoof_dir), 0)
#             # spoof_res = [False, 0.0, 0.0]

#             # embedding = face.embedding  # Expected to be a numpy array
#             # if embedding is None:
#             #     continue
#             # matches = verification(embedding)

#             compreface_result = formatter(face, "Unknown", 0.0, spoof_res, elapsed_time=0)
#             compreface_results.append(compreface_result)

#     return compreface_results


def detect_faces(img):
    """
    Runs face detection only (without recognition).
    Returns a list of detected face objects.
    """
    faces = analy_app.get(img, max_num=0)  # Runs both detection and recognition by default
    return faces

def recognize_faces(img, faces):
    """
    Runs recognition separately for already detected faces.
    """
    for face in faces:
        rec_handler.get(img, face)  # Apply recognition model
    return faces



def run_buffalo(frame):
    # Run face detection and recognition

    # Step 1: Detect faces
    detected_faces = detect_faces(frame)
    # print(f"Detected {len(detected_faces)} faces.")

    # Step 2: Recognize faces
    recognized_faces = recognize_faces(frame, detected_faces)
    # print(f"rec {recognized_faces}")
    compreface_results = []
    # For each detected face, store the embedding in the DB
    if recognized_faces is not None:
        for face in recognized_faces:
            # spoof_res = test(frame, face.bbox, str(spoof_dir), 0)
            spoof_res = [False, 0.0, 0.0]

            embedding = face.embedding  # Expected to be a numpy array
            if embedding is None:
                print("no embedding generated")
                continue
            matches = verification(embedding)

            # Ensure matches exist before accessing
            if not matches:
                print("No match found")
                continue  # Skip to the next face
            # print(f"faces {face}")
            compreface_result = formatter(face, matches[0]["subject_name"], matches[0]["distance"], spoof_res, elapsed_time=0)
            compreface_results.append(compreface_result)

    return compreface_results

# # Store all face crops in a batch
# batch_faces = []
# for face in faces:
#     x1, y1, x2, y2 = [int(c) for c in face.bbox]
#     face_crop = frame[y1:y2, x1:x2]  # Extract face region
#     face_crop = cv2.resize(face_crop, (112, 112))  # Resize for model
#     face_crop = face_crop.transpose(2, 0, 1)  # Convert HWC → CHW
#     batch_faces.append(face_crop)

# # Convert batch to NumPy array (B, C, H, W)
# batch_faces = np.array(batch_faces, dtype=np.float32) / 255.0  # Normalize
# batch_faces = np.expand_dims(batch_faces, axis=0)  # Add batch dimension if needed