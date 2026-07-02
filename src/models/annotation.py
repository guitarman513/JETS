from uuid import UUID, uuid4
from enum import StrEnum
from typing import List, Tuple, Dict
from pathlib import Path
from pydantic import BaseModel, Field

from models.z_model_hierarchy import InstantlyUpdates


    
    # @classmethod
    # def load_from_file(cls, drawing_folder_path: Path):
    #     drawing_info_path = drawing_folder_path / "drawing.json"
    #     if not drawing_info_path.exists():
    #         raise FileNotFoundError(f"Drawing info file not found at {drawing_info_path}.")
    #     return cls.model_validate_json(drawing_info_path.read_text())

# def get_all_drawings_in_project(project: ProjectInfo) -> list[Drawing]:
#     drawing_directory = project.this_project_folder_path / "drawings"
#     drawings: list[Drawing] = []
#     if not drawing_directory.exists():
#         return drawings
#     for drawing_folder in drawing_directory.iterdir():
#         if not drawing_folder.is_dir():
#             continue
#         try:
#             UUID(drawing_folder.name)
#         except ValueError:
#             continue
#         drawings.append(
#             Drawing.load_from_file(drawing_folder)
#         )
#     return drawings











# #TODO: I don't think I want to support text yet
# class AnnotationText(BaseModel):
#     xy_points: List[Dict]
class XYPoint(BaseModel):
    xy_coordinate: Tuple[float, float]
    is_vertex_counted_as_cnt: bool

class AnnotationHighlighter(BaseModel):
    xy_points: List[XYPoint] # TODO: handle smooth lines later?

class AnnotationLength(BaseModel):
    class LengthCoordinate(BaseModel):
        xy_coordinate: Tuple[float, float]
        is_vertex_counted_as_cnt: bool
    xy_points: List[LengthCoordinate] # "xy_points": [{"coords": [0,0], "is_vertex_counted_as_cnt":true},]

class AnnotationCount(BaseModel):
    xy_points: List[XYPoint] # "xy_points": [ [0,0], [1,1], [2,2], ]

# class AnnotationType(Enum):
#     # TEXT = "TEXT"
#     HIGHLIGHTER = "AnnotationHighlighter"
#     LENGTH = "AnnotationLength" # really this is a poly line
#     COUNT = "AnnotationCount" # can be multiple clicks 

class AnnotationShape(StrEnum):
    CIRCLE = "CIRCLE" #TODO: maybe only implement circle for now
    TRIANGLE = "TRIANGLE"
    SQUARE = "SQUARE"
    X = "X"

class AnnotationLineStyle(StrEnum):
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

DEFAULT_ANNOTATION_STYLES:List[AnnotationStyle] = [
        annotation_style_fire_alarm,
        annotation_style_branch_circuits
]

class AnnotationStyles(InstantlyUpdates):
    PARENT_PATH:Path = str("EDIT_ME_PLEASE")
    OUTPUT_CONFIG_FILE_NAME:str = "annotation_styles.json"
    annotation_styles: List[AnnotationStyle] = DEFAULT_ANNOTATION_STYLES

#TODO: save this to the defaults folder, and then copy it to the .jets user data directory in an 
# default_annotation_styles.json file that users may edit.



'''
Project Manager should only have to load data for one pdf at a time I guess
only need to auto-update one dwg at a time


'''

class DrawingScale(BaseModel):
    pass

class Drawing(InstantlyUpdates):
    PARENT_PATH:Path = str("EDIT_ME_PLEASE") # e.g. C:/Users/.../projects/some_project/drawings/uuid4uuid4-uuid4-uuid4-uuid4uuid4
    OUTPUT_CONFIG_FILE_NAME:str = "drawings.json" # drawing.json
    drawing_id: UUID = Field(default_factory=uuid4)
    dwg_filename: str           # user-friendly filename e.g. "E-101.pdf"
    thumbnail_plain_filename:str
    thumbnail_annotated_filename:str
    annotations: List[Annotation]
    dwg_scale: DrawingScale