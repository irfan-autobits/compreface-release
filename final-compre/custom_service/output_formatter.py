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