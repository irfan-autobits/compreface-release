import cv2
import insightface

app = insightface.app.FaceAnalysis(name="buffalo_l", providers=['CUDAExecutionProvider'])
app.prepare(ctx_id=0)

image_path = "/home/autobits/Autobits-emp-att/web-cli/final-compre/Test_vis/salman_khan.jpg"
image = cv2.imread(image_path)

faces = app.get(image, max_num=0)  # Extract all faces
print(f"Total Faces Detected: {len(faces)}")
print("----------------------------------------------------")
for face in faces:
    print(f"BBox: {face.bbox}")
    print(f"kps: {face.kps}")
    print(f"det_score: {face.det_score}")
    print(f"landmark_3d_68: {face.landmark_3d_68[:5]}")  
    print(f"pose: {face.pose}")  
    print(f"landmark_2d_106: {face.landmark_2d_106[:5]}")  
    print(f"gender: {face.gender}")  
    print(f"age: {face.age}")  
    print(f"Embedding: {face.embedding[:5]}")  # Print first 5 elements