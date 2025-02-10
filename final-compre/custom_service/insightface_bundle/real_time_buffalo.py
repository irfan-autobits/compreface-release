from insightface.app import FaceAnalysis
import numpy as np
from custom_service.insightface_bundle.verify_euclidean_dis import verify_identity
from app.models.model import Raw_Embedding, db
from flask import current_app      

# Initialize the InsightFace app with detection and recognition modules.
analy_app = FaceAnalysis(allowed_modules=['detection', 'recognition'])
analy_app.prepare(ctx_id=0, det_size=(640, 640))

def verification(input_embedding):
    # Example usage with known embeddings from the database
    with current_app.app_context():
        embeddings = Raw_Embedding.query.all()
        
        # List of known embeddings from the database (you need to format this appropriately)
        known_embeddings = [{'subject_name': emb.subject_name, 'embedding': np.array(emb.embedding)} for emb in embeddings]
                
        # Get the top 3 closest matches
        matches = verify_identity(input_embedding, known_embeddings, top_n=1)
        return matches

def formatter(face, sub_nam, distance, elapsed_time=0):
    
    bbox = face.bbox
    landms = face.kps
    confidence = face.det_score
    age = face.age if hasattr(face, "age") else None
    gender = face.gender if hasattr(face, "gender") else None
    embedding = face.embedding.tolist() if hasattr(face, "embedding") else []

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

def run_buffalo(frame):
    # Run face detection and recognition
    faces = analy_app.get(frame)
    compreface_results = []

    # For each detected face, store the embedding in the DB
    if faces is not None:
        for face in faces:
            embedding = face.embedding  # Expected to be a numpy array
            if embedding is None:
                continue
            matches = verification(embedding)
            if matches:
                for match in matches:
                    print(f"Match found {face.det_score}: {match['subject_name']} with distance {match['distance']}")
            
            compreface_result = formatter(face, matches[0]['subject_name'], matches[0]['distance'], elapsed_time=0)
            compreface_results.append(compreface_result)

    return compreface_results
