import logging
import cv2
import numpy as np
from time import time
from typing import List

# Replace with your actual implementation of BoundingBoxDTO and plugin_result
from custom_service.DTOs.bounding_box import BoundingBoxDTO
from custom_service.imgtools.imgscaler import ImgScaler
from custom_service.add_on import base, mixins
from custom_service.imgtools.types import Array3D
from cached_property import cached_property
import collections

import ctypes
logger = logging.getLogger(__name__)
libc = ctypes.CDLL("libc.so.6")

import mxnet as mx

from insightface.app import FaceAnalysis
from insightface.model_zoo import (model_store, face_detection,
                                face_recognition, face_genderage)
from insightface.utils import face_align

class DetectionOnlyFaceAnalysis(FaceAnalysis):
    rec_model = None
    ga_model = None

    def __init__(self, file):
        self.det_model = face_detection.FaceDetector(file, 'net3')

IMG_LENGTH_LIMIT = 640
GPU_IDX = 0

class InsightFaceMixin:
    _CTX_ID = GPU_IDX
    _NMS = 0.4

    def get_model_file(self, ml_model: base.MLModel):
        if not ml_model.exists():
            raise f'Model {ml_model.name} does not exists'
        return model_store.find_params_file(ml_model.path)
    

class Calculator(InsightFaceMixin, mixins.CalculatorMixin, base.BasePlugin):
    ml_models = (
        ('arcface_mobilefacenet', '17TpxpyHuUc1ZTm3RIbfvhnBcZqhyKszV', (1.26538905, 5.552089201), 200),
        ('arcface_r100_v1', '11xFaEHIQLNze3-2RUV1cQfT-q6PKKfYp', (1.23132175, 6.602259425), 400),
        ('arcface_resnet34', '1ECp5XrLgfEAnwyTYFEhJgIsOAw6KaHa7', (1.2462842, 5.981636853), 400),
        ('arcface_resnet50', '1a9nib4I9OIVORwsqLB0gz0WuLC32E8gf', (1.2375747, 5.973354538), 400),
        ('arcface-r50-msfdrop75', '1gNuvRNHCNgvFtz7SjhW82v2-znlAYaRO', (1.2350148, 7.071431642), 400),
        ('arcface-r100-msfdrop75', '1lAnFcBXoMKqE-SkZKTmi6MsYAmzG0tFw', (1.224676, 6.322647217), 400),
        # CASIA-WebFace-Masked, 0.9840 LFW, 0.9667 LFW-Masked (orig mobilefacenet has 0.9482 on LFW-Masked)
        ('arcface_mobilefacenet_casia_masked', '1ltcJChTdP1yQWF9e1ESpTNYAVwxLSNLP', (1.22507105, 7.321198934), 200),
    )

    def calc_embedding(self, face_img: Array3D) -> Array3D:
        return self._calculation_model.get_embedding(face_img).flatten()

    @cached_property
    def _calculation_model(self):
        model_file = self.get_model_file(self.ml_model)
        model = face_recognition.FaceRecognition(
            self.ml_model.name, True, model_file)
        model.prepare(ctx_id=self._CTX_ID)
        return model

class FaceDetector(InsightFaceMixin, mixins.FaceDetectorMixin, base.BasePlugin):
    ml_models = (
        ('retinaface_mnet025_v1', '1ggNFFqpe0abWz6V1A82rnxD6fyxB8W2c'),
        ('retinaface_mnet025_v2', '1EYTMxgcNdlvoL1fSC8N1zkaWrX75ZoNL'),
        ('retinaface_r50_v1', '1LZ5h9f_YC5EdbIZAqVba9TKHipi90JBj'),
    )
    call_counter = 0
    MAX_CALL_COUNTER = 1000
    IMG_LENGTH_LIMIT = IMG_LENGTH_LIMIT
    IMAGE_SIZE = 112
    det_prob_threshold = 0.8

    @cached_property
    def _detection_model(self):
        model_file = self.get_model_file(self.ml_model)
        model = DetectionOnlyFaceAnalysis(model_file)
        model.prepare(ctx_id=self._CTX_ID, nms=self._NMS)
        return model

    def find_faces(self, img: Array3D, det_prob_threshold: float = None) -> List[BoundingBoxDTO]:
        assert 0 <= det_prob_threshold <= 1
        scaler = ImgScaler(self.IMG_LENGTH_LIMIT)
        img = scaler.downscale_img(img)    

        if skip:
            Face = collections.namedtuple('Face', [
                'bbox', 'landmark', 'det_score', 'embedding', 'gender', 'age', 'embedding_norm', 'normed_embedding'])
            ret = []
            bbox = np.ndarray(shape=(4,), buffer=np.array([0, 0, float(img.shape[1]), float(img.shape[0])]), dtype=float)
            det_score = 1.0
            landmark = np.ndarray(shape=(5, 2), buffer=np.array([[float(img.shape[1]), 0.], [0., 0.], [0., 0.], [0., 0.], [0., 0.]]),
                                  dtype=float)
            face = Face(bbox=bbox, landmark=landmark, det_score=det_score, embedding=None, gender=None, age=None, normed_embedding=None, embedding_norm=None)
            ret.append(face)
            results = ret
            det_prob_threshold = self.det_prob_threshold
        else:
            model = self._detection_model
            results = model.get(img, det_thresh=det_prob_threshold)        

        boxes = []

        self.call_counter +=1
        if self.call_counter % self.MAX_CALL_COUNTER == 0:
            libc.malloc_trim(0)
            self.call_counter = 0            
            
        for result in results:
            downscaled_box_array = result.bbox.astype(np.int).flatten()
            downscaled_box = BoundingBoxDTO(x_min=downscaled_box_array[0],
                                            y_min=downscaled_box_array[1],
                                            x_max=downscaled_box_array[2],
                                            y_max=downscaled_box_array[3],
                                            probability=result.det_score,
                                            np_landmarks=result.landmark)
            box = downscaled_box.scaled(scaler.upscale_coefficient)
            if box.probability <= det_prob_threshold:
                logger.debug(f'Box Filtered out because below threshold ({det_prob_threshold}: {box})')
                continue
            logger.debug(f"Found: {box}")
            boxes.append(box)
        return boxes

    def crop_face(self, img: Array3D, box: BoundingBoxDTO) -> Array3D:
        return face_align.norm_crop(img, landmark=box._np_landmarks,
                                    image_size=self.IMAGE_SIZE)            