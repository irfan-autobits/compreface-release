from abc import ABC, abstractmethod
from typing import List

import numpy as np

from custom_service.DTOs.bounding_box import BoundingBoxDTO
from custom_service.DTOs.plugin_result import FaceDTO, EmbeddingDTO
from custom_service.imgtools.types import Array3D
from custom_service.add_on.managers import plugin_manager


class FaceScanner(ABC):
    ID = None

    def __init__(self):
        assert self.ID

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FaceScanner, cls).__new__(cls)
        return cls.instance

    @abstractmethod
    def scan(self, img: Array3D, det_prob_threshold: float = None) -> List[FaceDTO]:
        """ Find face bounding boxes and calculate embeddings"""
        raise NotImplementedError

    @abstractmethod
    def find_faces(self, img: Array3D, det_prob_threshold: float = None) -> List[BoundingBoxDTO]:
        """ Find face bounding boxes, without calculating embeddings"""
        raise NotImplementedError

    @property
    @abstractmethod
    def difference_threshold(self) -> float:
        """ Difference threshold between two embeddings"""
        raise NotImplementedError


class ScannerWithPluggins(FaceScanner):
    """
    Class for backward compatibility.
    The scanner only performs face detection and embedding calculation.
    """
    ID = "ScannerWithPlugins"

    def scan(self, img: Array3D, det_prob_threshold: float = None):
        
        return plugin_manager.detector(img, det_prob_threshold,
                                       [plugin_manager.calculator])

    def find_faces(self, img: Array3D, det_prob_threshold: float = None) -> List[BoundingBoxDTO]:
        return plugin_manager.detector.find_faces(img, det_prob_threshold)

    @property
    def difference_threshold(self):
        return plugin_manager.calculator.ml_model.difference_threshold


class MockScanner(FaceScanner):
    ID = 'MockScanner'

    def scan(self, img: Array3D, det_prob_threshold: float = None) -> List[FaceDTO]:
        return [FaceDTO(box=BoundingBoxDTO(0, 0, 0, 0, 0),
                        plugins_dto=[EmbeddingDTO(embedding=np.random.rand(1))],
                        img=img, face_img=img)]

    def find_faces(self, img: Array3D, det_prob_threshold: float = None) -> List[BoundingBoxDTO]:
        return [BoundingBoxDTO(0, 0, 0, 0, 0)]
