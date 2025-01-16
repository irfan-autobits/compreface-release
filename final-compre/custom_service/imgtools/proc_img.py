from typing import Tuple

from skimage import transform

from custom_service.DTOs.bounding_box import BoundingBoxDTO
from custom_service.imgtools.types import Array3D


def crop_img(img: Array3D, box: BoundingBoxDTO) -> Array3D:
    return img[box.y_min:box.y_max, box.x_min:box.x_max, :]


def squish_img(img: Array3D, dimensions: Tuple[int, int]) -> Array3D:
    return transform.resize(img, dimensions)
