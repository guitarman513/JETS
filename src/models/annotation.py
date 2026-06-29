from uuid import UUID, uuid4
from enum import Enum
from typing import List, Tuple, Dict

from pydantic import BaseModel, Field


# #TODO: I don't think I want to support text yet
# class AnnotationText(BaseModel):
#     xy_points: List[Dict]
class AnnotationHighlighter(BaseModel):
    xy_points: List[Dict] # TODO: handle smooth lines later?

class AnnotationLength(BaseModel):
    xy_points: List[Dict] # "xy_points": [{"coords": [0,0], "is_vertex_counted_as_cnt":true},]

class AnnotationCount(BaseModel):
    xy_points: List[Tuple[float, float]] # "xy_points": [ [0,0], [1,1], [2,2], ]

class AnnotationType(Enum):
    # TEXT = "TEXT"
    HIGHLIGHTER = "AnnotationHighlighter"
    LENGTH = "AnnotationLength" # really this is a poly line
    COUNT = "AnnotationCount" # can be multiple clicks 

class AnnotationShape(Enum):
    CIRCLE = "CIRCLE" #TODO: maybe only implement circle for now
    TRIANGLE = "TRIANGLE"
    SQUARE = "SQUARE"
    X = "X"

class AnnotationLineStyle(Enum):
    SOLID = "SOLID"
    DASHED = "DASHED"

class AnnotationStyle(BaseModel):
    name: str
    count_color_outer: str # these color strings will be 6-character hex I guess. Maybe there is a better datatype to use here idk
    count_color_inner: str
    count_size: float
    count_shape: AnnotationShape
    count_opacity: float

    length_color: str
    length_width: float
    length_vertex_size: float
    length_vertex_shape: AnnotationShape
    length_opacity: float
    length_line_style: AnnotationLineStyle
    
    highlight_color: str
    highlight_width: float #TODO: probably just hard-code this
    highlight_opacity: float

    class Config:
        use_enum_values = True


class Annotation(BaseModel):
    annotation_id: UUID = Field(default_factory=uuid4)
    annotation_type: AnnotationType
    annotation_style: AnnotationStyle

    class Config:
        use_enum_values = True


