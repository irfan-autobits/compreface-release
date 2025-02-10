import cv2
import numpy as np
import onnxruntime as ort
# from config.Paths import MODELS_DIR

reco_model = f"custom_service/Pytorch_Retinaface/weights/R100_Glint360K.onnx"

def align_face(face_img, landmarks, output_size=(112, 112)):
    print("align face called -------------------------------------------------")
    face_img = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
    # Landmarks for left and right eyes (indices may vary; adjust based on RetinaFace's output)
    left_eye = landmarks[0]
    right_eye = landmarks[1]

    # Calculate center of eyes
    eyes_center = ((left_eye[0] + right_eye[0]) // 2, (left_eye[1] + right_eye[1]) // 2)

    # Calculate angle between eyes
    dy = right_eye[1] - left_eye[1]
    dx = right_eye[0] - left_eye[0]
    angle = np.degrees(np.arctan2(dy, dx))

    # Scale factor to match desired eye distance (adjust based on model training)
    desired_eye_distance = output_size[0] * 0.35  # ~35% of the image width
    current_eye_distance = np.hypot(dx, dy)
    scale = desired_eye_distance / current_eye_distance

    # Get rotation matrix
    M = cv2.getRotationMatrix2D(eyes_center, angle, scale)

    # Adjust translation to center the face
    tX = output_size[0] * 0.5
    tY = output_size[1] * 0.35  # ~35% from top
    M[0, 2] += (tX - eyes_center[0])
    M[1, 2] += (tY - eyes_center[1])

    # Apply affine transformation
    aligned_face = cv2.warpAffine(
        face_img, M, output_size, flags=cv2.INTER_LINEAR
    )

    return aligned_face

def preprocess(aligned_face):
    print("process called.....................................................................")
    # Convert to float32 and normalize
    aligned_face = aligned_face.astype(np.float32)
    aligned_face = (aligned_face - 127.5) * 0.0078125  # Scale to [-1, 1]

    # Change from HWC to CHW and add batch dimension
    aligned_face = np.transpose(aligned_face, (2, 0, 1))  # CHW
    aligned_face = np.expand_dims(aligned_face, axis=0)   # BCHW
    print("returned align face")
    return aligned_face

# Initialize ONNX Runtime session
ort_session = ort.InferenceSession(
    str(reco_model)
    ,providers=['CUDAExecutionProvider', 'CPUExecutionProvider']  # Use GPU if available
)

# In your get_embedding function:
def get_embedding(aligned_face):
    try:
        input_name = ort_session.get_inputs()[0].name
        embedding = ort_session.run(None, {input_name: aligned_face})[0]
        return embedding.flatten().tolist()  # Convert to list for database storage
    except Exception as e:
        print(f"Embedding generation failed: {str(e)}")
        return None
    
# Normalize embedding to unit vector for cosine similarity
def normalize_embedding(embedding):
    return embedding / np.linalg.norm(embedding)
