# import time
from insightface.app import FaceAnalysis
# import numpy as np
# from custom_service.insightface_bundle.verify_euclidean_dis import verify_identity
# from app.models.model import Raw_Embedding, db
# from flask import current_app      
# from config.logger_config import cam_stat_logger , console_logger, exec_time_logger

# from custom_service.insightface_bundle.recog_split import recognize_faces
# from custom_service.insightface_bundle.silent_antispoof.real_time_antispoof import test
# from config.Paths import MODELS_DIR, model_pack_name
# from custom_service.output_formatter import formatter

# spoof_dir = MODELS_DIR / "anti_spoof_models"
# # Initialize the InsightFace app with detection and recognition modules.
# analy_app = FaceAnalysis(name=model_pack_name ,allowed_modules=['detection', 'landmark_3d_68'])
# analy_app.prepare(ctx_id=0, det_size=(640, 640))


# def verification(input_embedding):
#     # Example usage with known embeddings from the database
#     with current_app.app_context():
#         embeddings = Raw_Embedding.query.all()
        
#         # List of known embeddings from the database (you need to format this appropriately)
#         known_embeddings = [{'subject_name': emb.subject_name, 'embedding': np.array(emb.embedding)} for emb in embeddings]
                
#         # Get the top 3 closest matches
#         matches = verify_identity(input_embedding, known_embeddings, top_n=1)
#         return matches



# def detect_faces(img):
#     """
#     Runs face detection only (without recognition).
#     Returns a list of detected face objects.
#     """
#     faces = analy_app.get(img, max_num=0)  # Runs both detection and recognition by default
#     return faces

# def run_buffalo(frame):
#     # Run face detection and recognition

#     # Step 1: Detect faces
#     start_time = time.time()  # Start timing before reading the frame
#     detected_faces = detect_faces(frame)
#     frame_time = time.time() - start_time 
#     exec_time_logger.debug(f"det {frame_time:.4f} seconds")    
#     # print(f"Detected {len(detected_faces)} faces.")

#     # Step 2: Recognize faces
#     # Step 1: Detect faces
#     start_time = time.time()  # Start timing before reading the frame
#     recognized_faces = recognize_faces(frame, detected_faces, mode='local') # remote
#     frame_time = time.time() - start_time 
#     exec_time_logger.debug(f"rec {frame_time:.4f} seconds")      
#     # print(f"rec {recognized_faces}")
#     compreface_results = []
#     # For each detected face, store the embedding in the DB
#     if recognized_faces is not None:
#         for face in recognized_faces:
#             # spoof_res = test(frame, face.bbox, str(spoof_dir), 0)
#             spoof_res = [False, 0.0, 0.0]

#             embedding = face.embedding  # Expected to be a numpy array
#             if embedding is None:
#                 print("no embedding generated")
#                 continue
#             matches = verification(embedding)

#             # Ensure matches exist before accessing
#             if not matches:
#                 print("No match found")
#                 continue  # Skip to the next face
#             # print(f"faces {face}")
#             compreface_result = formatter(face, matches[0]["subject_name"], matches[0]["distance"], spoof_res, elapsed_time=0)
#             compreface_results.append(compreface_result)

#     return compreface_results
