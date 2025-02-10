import shutil
import traceback
import cv2
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import numpy as np
from sqlalchemy.dialects.postgresql import UUID, ARRAY
import uuid

from insightface.utils import face_align
import torch
# from custom_service.Pytorch_Retinaface.pytorch_insightface import align_face, preprocess, get_embedding, normalize_embedding
from custom_service.Pytorch_Retinaface.Real_time_detector import FaceDetectorRetinaFace
from custom_service.Pytorch_Retinaface.calculator import get_face_embedding
from pathlib import Path

app = Flask(__name__)
# Define the base directory as the directory where the script is located
BASE_DIR = Path(__file__).resolve().parent
SUBJECT_DIR = BASE_DIR / "custom_service" / "Pytorch_Retinaface" / "subjects_img" / "train"
MODELS_DIR = BASE_DIR / ".models"
RES_DIR = BASE_DIR / "Test_res"

shutil.rmtree(RES_DIR, ignore_errors=True)
RES_DIR.mkdir(parents=True, exist_ok=True)

vis_thres = 0.6
cpu = False
device = torch.device("cpu" if cpu else "cuda")

# Initialize model once at startup
model_path = str(MODELS_DIR / "glint360k_cosface_r100_fp16_0.1.pth")
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql+psycopg2://postgres:postgres@localhost:6432/frs"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

class Raw_Embedding(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    subject_name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(ARRAY(db.Float), nullable=False)
    calculator = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f"<Embedding {self.id}, Subject: {self.subject_name}>"

# Ensure tables are created
with app.app_context():
    db.create_all()
    print("Table created raw_embedding")

# def cal_embedding(face, landmarks):
#     try:
#         if face is None or face.size == 0:
#             return []
#         # Load the model
        
#         embedding_model = get_embedding_model(model_path, fp16=True)

#         # Read and preprocess an image
#         img = cv2.imread("sample_face.jpg")
#         preprocessed_img = preprocess(img)

#         # Extract face embedding
#         embedding = get_embedding(embedding_model, preprocessed_img)

#         print("Face embedding:", embedding)
#     except Exception as e:
#         print(f"Embedding Error: {str(e)}")
#         return []


# def cal_embedding(face, landmarks):
#     try:
#         if face is None or face.size == 0:
#             return []
            
#         # Align face
#         aligned_face = face_align.norm_crop(face, landmarks, image_size=112)
        
#         # Convert to RGB
#         aligned_face = cv2.cvtColor(aligned_face, cv2.COLOR_BGR2RGB)
        
#         # Preprocessing for the new model
#         aligned_face = (aligned_face.transpose(2, 0, 1) - 127.5) / 128.0  # Normalization
#         input_tensor = torch.FloatTensor(aligned_face).unsqueeze(0).to(device)
        
#         # Generate embedding
#         with torch.no_grad():
#             embedding = EMBEDDING_MODEL(input_tensor)[0].cpu().numpy()
        
#         # Normalize embedding
#         embedding = embedding / np.linalg.norm(embedding)
#         return embedding.tolist()
    
#     except Exception as e:
#         print(f"Embedding Error: {str(e)}")
#         return []
    
def store_embedding(subject_name, embedding_vector):
    # Create and store embedding in Raw_Embedding table
    embedding_entry = Raw_Embedding(
        subject_name=subject_name,
        embedding=embedding_vector,
        calculator="insightface_R_100"
    )
    
    db.session.add(embedding_entry)
    db.session.commit()
    
    return embedding_entry.id  # Return embedding ID for reference

def show_res(image_path, img_raw, dets, landms,text):
    dets = np.concatenate((dets, landms), axis=1)
    # show image
    for b in dets:
        if b[4] < vis_thres:
            continue
        b = list(map(int, b))
        cv2.rectangle(img_raw, (b[0], b[1]), (b[2], b[3]), (0, 255, 0), 2)
        cx = b[0]
        cy = b[1] + 12
        cv2.putText(img_raw, text, (cx, cy),
                    cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))

        # landms
        cv2.circle(img_raw, (b[5], b[6]), 1, (0, 0, 255), 4)
        cv2.circle(img_raw, (b[7], b[8]), 1, (0, 255, 255), 4)
        cv2.circle(img_raw, (b[9], b[10]), 1, (255, 0, 255), 4)
        cv2.circle(img_raw, (b[11], b[12]), 1, (0, 255, 0), 4)
        cv2.circle(img_raw, (b[13], b[14]), 1, (255, 0, 0), 4)
    
    # save image
    image_name = Path(image_path).name 
    name = "test.jpg"
    face_image_path = RES_DIR / image_name
    cv2.imwrite(str(face_image_path), img_raw)    

# trainind begin 
def process_images_with_retinaface():
    retina_detect = MODELS_DIR / "Resnet50_Final.pth"
    face_detector = FaceDetectorRetinaFace(model_path=str(retina_detect))

    # Supported image formats
    valid_extensions = (".jpg", ".jpeg", ".png")

    # Iterate over images in SUBJECT_DIR
    for image_path in SUBJECT_DIR.glob("*"):
        if image_path.suffix.lower() in valid_extensions:
            print(f"\nProcessing: {image_path}")
            
            # Extract subject name from filename (remove extension)
            subject_name = image_path.stem.replace("_", " ").title()

            # Read image in BGR format
            img_raw = cv2.imread(str(image_path), cv2.IMREAD_COLOR)

            if img_raw is None:
                print(f"Failed to read {image_path}")
                continue

            # Perform face detection
            dets, landms, elapsed_time = face_detector.detect(img_raw)

            for i, det in enumerate(dets):
                try:
                    if det[4] < vis_thres:
                        continue
                    x1, y1, x2, y2, confidence = map(float, det[:5])  # Use float for precision
                    landmarks = {
                        "left_eye": [float(landms[i][0]), float(landms[i][1])],
                        "right_eye": [float(landms[i][2]), float(landms[i][3])],
                        "nose": [float(landms[i][4]), float(landms[i][5])],
                        "right_mouth": [float(landms[i][6]), float(landms[i][7])],
                        "left_mouth": [float(landms[i][8]), float(landms[i][9])],
                    }
                    
                    # Convert to integers and ensure within image bounds
                    x1 = max(0, int(x1))
                    y1 = max(0, int(y1))
                    x2 = min(img_raw.shape[1], int(x2))
                    y2 = min(img_raw.shape[0], int(y2))

                    # Extract face region
                    face_region = img_raw[y1:y2, x1:x2]
                    # face_region = img_raw[int(y1):int(y2), int(x1):int(x2)]

                    if face_region.size == 0:
                        print(f"Invalid face region in detection {i+1}")
                        continue

                    # Convert landmarks to numpy array in correct order
                    # landmark_points = np.array([
                    #     landmarks[0],  # left eye
                    #     landmarks[1],  # right eye
                    #     landmarks[2],  # nose
                    #     landmarks[3],  # right mouth
                    #     landmarks[4]   # left mouth
                    # ], dtype=np.float32)
                    print("landmarks compeleted;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;")

                    # In your FaceDetectorRetinaFace class postprocessing
                    # Ensure landmarks are ordered as [left_eye, right_eye, nose, right_mouth, left_mouth]
                    landmark_points = landms[i].reshape(-1, 2)  # Shape: (5, 2)
                    print(f"model path is ---------- {model_path}")
                    embedding = get_face_embedding(model_path, face_region)
                    # Calculate embedding
                    # embedding = cal_embedding(face_region, landmark_points)
                    
                    if not embedding:
                        print(f"Failed to generate embedding for detection {i+1}")
                        continue
                    print("embedding shape::::::::::",embedding.shape)  
                    # Store embedding in database
                    embedding_id = store_embedding(subject_name, embedding)
                    print(f"Stored embedding for {subject_name} (ID: {embedding_id})")

                except Exception as e:
                    print(f"Error processing detection {i+1}: {str(e)}")
                    traceback.print_exc() 
                    continue

            # Visualization (keep your original show_res function if needed)
            show_res(image_path, img_raw, dets, landms,"Unknown")

    print("\nProcessing complete.")

# Run the function
process_images_with_retinaface()

if __name__ == "__main__":
    app.run(debug=True)
