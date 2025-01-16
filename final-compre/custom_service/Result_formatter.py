def convert_yunet_to_compreface(yunet_results):
    compreface_results = []

    for face in yunet_results:
        compreface_result = {
            "age": {
                "probability": None,  # Age is not available in yunet; can be set to None or a default
                "high": None,        # High age prediction
                "low": None          # Low age prediction
            },
            "gender": {
                "probability": None,  # Gender is not available in yunet
                "value": None         # Gender value
            },
            "mask": {
                "probability": None,  # Mask prediction is not available in yunet
                "value": None         # Mask value
            },
            "embedding": [],          # Yunet does not provide embeddings
            "box": {
                "probability": face.get("confidence", 0),  # Confidence becomes the probability
                "x_max": face["x2"],                      # Map bounding box coordinates
                "y_max": face["y2"],
                "x_min": face["x1"],
                "y_min": face["y1"]
            },
            "landmarks": [
                face["landmarks"].get("left_eye"),
                face["landmarks"].get("right_eye"),
                face["landmarks"].get("nose"),
                face["landmarks"].get("right_mouth"),
                face["landmarks"].get("left_mouth")
            ],
            "subjects": [],            # Yunet does not provide subject similarity data
            "execution_time": {
                "age": None,          # Yunet does not provide execution time details
                "gender": None,
                "detector": None,
                "calculator": None,
                "mask": None
            }
        }

        compreface_results.append(compreface_result)

    return compreface_results


def process_detection_dto(face_dto):
    compreface_results = []

    for face in face_dto:
        # Adjust access to the FaceDTO object's attributes
        compreface_result = {
            "box": {
                "probability": face.box.probability,
                "x_max": face.box.x_max,
                "y_max": face.box.y_max,
                "x_min": face.box.x_min,
                "y_min": face.box.y_min
            },
            "landmarks": [
                face.box._np_landmarks[0],
                face.box._np_landmarks[1],
                face.box._np_landmarks[2],
                face.box._np_landmarks[3],
                face.box._np_landmarks[4]
            ],
            "subjects": [],
            "execution_time": {
                "age": None,
                "gender": None,
                "detector": face.execution_time,
                "calculator": None,
                "mask": None
            }
        }
        compreface_results.append(compreface_result)

    return compreface_results


def process_face_dto(face_dto, scan_id):
    compreface_results = []

    for face in face_dto:
        # Adjust access to the FaceDTO object's attributes
        compreface_result = {
            "box": {
                "probability": face.box.probability,
                "x_max": face.box.x_max,
                "y_max": face.box.y_max,
                "x_min": face.box.x_min,
                "y_min": face.box.y_min
            },
            "landmarks": [
                face.box._np_landmarks[0],
                face.box._np_landmarks[1],
                face.box._np_landmarks[2],
                face.box._np_landmarks[3],
                face.box._np_landmarks[4]
            ],
            "subjects": [],
            "execution_time": {
                "age": None,
                "gender": None,
                "detector": face.execution_time,
                "calculator": None,
                "mask": None
            }
        }
        compreface_results.append(compreface_result)

    return compreface_results