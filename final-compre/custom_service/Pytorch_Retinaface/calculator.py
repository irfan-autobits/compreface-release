import cv2
import numpy as np
import insightface
from insightface.app import FaceAnalysis

GPU_IDX = 0 # for gpu support 

# Initialize FaceAnalysis for recognition (make sure to specify 'recognition' modules)
app = FaceAnalysis(allowed_modules=['recognition'])  # Only enable the recognition model

# Load the custom ONNX model (if you have it)
handler = insightface.model_zoo.get_model('glint360k_cosface_r100.onnx')
handler.prepare(ctx_id=GPU_IDX)

dets = None
# Generate embeddings for detected faces
embeddings = []
for face in dets:
    embedding = handler.get_embedding(face)  # Get the embedding
    embeddings.append(embedding)

# Now `embeddings` will contain the generated embeddings for each detected face
print("Generated Embeddings:", embeddings)
