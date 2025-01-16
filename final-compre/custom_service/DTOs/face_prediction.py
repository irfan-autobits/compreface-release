import attr

from custom_service.DTOs.bounding_box import BoundingBoxDTO
from custom_service.DTOs.json_encodable import JSONEncodable

@attr.s(auto_attribs=True, frozen=True)
class NamePrediction(JSONEncodable):
    face_name: str = attr.ib(converter=str)
    probability: float = attr.ib(converter=float)


@attr.s(auto_attribs=True, frozen=True)
class FacePrediction(NamePrediction):
    box: BoundingBoxDTO
