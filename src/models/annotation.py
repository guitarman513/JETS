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
    class LengthCoordinate(BaseModel):
        xy_coordinate: Tuple[float, float]
        is_vertex_counted_as_cnt: bool
    xy_points: List[LengthCoordinate] # "xy_points": [{"coords": [0,0], "is_vertex_counted_as_cnt":true},]

class AnnotationCount(BaseModel):
    xy_points: List[Tuple[float, float]] # "xy_points": [ [0,0], [1,1], [2,2], ]

# class AnnotationType(Enum):
#     # TEXT = "TEXT"
#     HIGHLIGHTER = "AnnotationHighlighter"
#     LENGTH = "AnnotationLength" # really this is a poly line
#     COUNT = "AnnotationCount" # can be multiple clicks 

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
    annotation_type: AnnotationHighlighter | AnnotationLength | AnnotationCount
    annotation_style: AnnotationStyle
    class Config:
        use_enum_values = True

annotation_style_fire_alarm = AnnotationStyle(
    name="FIRE ALARM", count_color_outer="FF0000", count_color_inner="FF1111", count_size=5, count_shape=AnnotationShape.CIRCLE, count_opacity=0.8,
    length_color="FA0000", length_width=4, length_vertex_size=5, length_vertex_shape=AnnotationShape.CIRCLE, length_opacity=0.9, length_line_style=AnnotationLineStyle.SOLID,
    highlight_color="EEEEEF", highlight_width=10, highlight_opacity=0.4
)
annotation_style_branch_circuits = AnnotationStyle(
    name="BRANCH CIRCUITS", count_color_outer="FF0000", count_color_inner="FF1111", count_size=5, count_shape=AnnotationShape.CIRCLE, count_opacity=0.8,
    length_color="FA0000", length_width=4, length_vertex_size=5, length_vertex_shape=AnnotationShape.CIRCLE, length_opacity=0.9, length_line_style=AnnotationLineStyle.SOLID,
    highlight_color="EEEEEF", highlight_width=10, highlight_opacity=0.4
)

#TODO: save this to the defaults folder, and then copy it to the .jets user data directory in an 
# default_annotation_styles.json file that users may edit.
default_annotation_styles = [
    annotation_style_fire_alarm, 
    annotation_style_branch_circuits
]