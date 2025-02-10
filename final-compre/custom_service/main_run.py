import traceback
from flask import jsonify
import numpy as np
from custom_service.Result_formatter import convert_yunet_to_compreface, process_face_dto, process_detection_dto
from custom_service.add_on.yunet_detection import FaceDetectorYunet
from config.Paths import MODELS_DIR
# from custom_service.add_on.managers import plugin_manager
from custom_service.add_on import managers
from custom_service.scanner.facescanners import scanner
from config.logger_config import cam_stat_logger , console_logger, exec_time_logger, det_logger
from custom_service.imgtools.read_img import read_img
from custom_service.imgtools.files import IMG_DIR

# retinaface imports
# from custom_service.Pytorch_Retinaface.Real_time_detector import FaceDetectorRetinaFace
from custom_service.insightface_bundle.real_time_buffalo import run_buffalo

# from custom_service.pytorch_arcface.recognition import cal_embedding

def yunet_detect(frame):
    yunet_detect = MODELS_DIR / "face_detection_yunet_2023mar.onnx"

    face_detector = FaceDetectorYunet(model_path=str(yunet_detect), img_size=(300, 300), threshold=0.5)

    try:
        faces = face_detector.detect(frame)
        # frame = face_detector.draw_faces(frame, faces, draw_landmarks=False, show_confidence=True)
        compreface_results = convert_yunet_to_compreface(faces)
    except Exception as e:
        print(e)
        compreface_results = []

    return compreface_results

# def RetinaFace_detect(frame):
#     retina_detect = MODELS_DIR / "Resnet50_Final.pth"
#     # Initialize RetinaFace Detector
#     face_detector = FaceDetectorRetinaFace(model_path=str(retina_detect))
#     try:
#         # Run RetinaFace detection
#         compreface_results = face_detector.detect(frame)
#     except Exception as e:
#         print(e)
#         compreface_results = []   
#     return compreface_results
         
def insightface_buffalo(frame):
    try:
        compreface_results = run_buffalo(frame)
    except Exception as e:
        print(e)
        compreface_results = []   
    return compreface_results
    
DET_PROB_THRESHOLD = 0.8
# frame_bgr = frame_rgb[..., ::-1]  # Convert RGB to BGR

def init_model() -> None:
    detector = managers.plugin_manager.detector
    face_plugins = managers.plugin_manager.face_plugins
    detector(
        img=read_img(str(IMG_DIR / 'einstein.jpeg')),
        det_prob_threshold= DET_PROB_THRESHOLD,
        face_plugins=face_plugins
    )
    print("Starting to load ML models")
    return None

def find_faces_post(frame):
    try:
        detector = managers.plugin_manager.detector
        faces = detector(
            img=frame,
            det_prob_threshold= DET_PROB_THRESHOLD,
            face_plugins= []
        )
        det_logger.info(f"returned faces-----------:{faces}")
        compreface_results = process_detection_dto(faces)
        print(f"formatted {compreface_results}")
    except Exception as e:
        print(e)
        traceback.print_exc() 
        compreface_results = []

    return compreface_results

def scan_faces_post(frame):
    try:
        faces = scanner.scan(
            img=frame,
            det_prob_threshold= DET_PROB_THRESHOLD
        )
        det_logger.info(f"returned faces-----------:{faces}")
        # compreface_results = process_face_dto(faces, scanner.ID)
        print(f"formatted {compreface_results}")
    except Exception as e:
        print(e)
        compreface_results = []

    return compreface_results