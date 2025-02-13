import cv2
from insightface.app import FaceAnalysis
import numpy as np
np.int = int
model_zoo = ['buffalo_l', 'buffalo_m', 'buffalo_s']
model_pack_name = model_zoo[2]  # Using 'buffalo_s'

# Enable all available modules
app = FaceAnalysis(name=model_pack_name, allowed_modules=['detection', 'landmark_2d_106', 'landmark_3d_68', 'genderage', 'recognition'])

# Prepare the model (Ensure CUDA is available, otherwise use CPU)
app.prepare(ctx_id=0, det_size=(640, 640))

# Load and process image
image_path = "./train/salman_khan.jpg"
image = cv2.imread(image_path)
faces = app.get(image, max_num=0)  # Extract all faces
dimg = app.draw_on(image, faces)
# dimg = cv2.cvtColor(dimg, cv2.COLOR_BGR2RGB)

cv2.imshow("detimg", dimg)
cv2.imwrite("detimg.jpg", dimg)
# Print results
print(f"Total Faces Detected: {len(faces)}")
print("----------------------------------------------------")
for face in faces:
    if face.bbox is not None:
        print(f"BBox: {face.bbox}")
    if face.kps is not None:
        print(f"kps: {face.kps}")
    if face.det_score is not None:
        print(f"det_score: {face.det_score}")
    if face.landmark_3d_68 is not None:
        print(f"landmark_3d_68: {face.landmark_3d_68[:5]}")  
    if face.pose is not None:
        print(f"pose: {face.pose}")  
    if face.landmark_2d_106 is not None:
        print(f"landmark_2d_106: {face.landmark_2d_106[:5]}")  
    if face.gender is not None:
        print(f"gender: {face.gender}")  
    if face.age is not None:
        print(f"age: {face.age}")  
    if face.embedding is not None:
        print(f"Embedding: {face.embedding[:5]}")  # Print first 5 elements
