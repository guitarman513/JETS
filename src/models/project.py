from typing import List, Dict, Any
from time import time
from pathlib import Path
import json

from pydantic import BaseModel

from models.annotation import AnnotationStyle, AnnotationShape, AnnotationLineStyle
from models.a_defaults import DEFAULT_PROJECTS_PATH

class ProjectQuickInfo(BaseModel):
    project_name: str
    created: int
    last_updated: int
    drawing_order: List[str]
    directory_path: Path

    class Config:
        json_encoders = {Path: str}



#TODO: look at chatGPT chat with changes for this.




#TODO: EDIT BELOW 
def create_default_project(project_name:str = "default_project"):
    '''
    Create:
    - Project directory in defaults/default_project
    - Default AnnotationStyle objects in annotation_styles.json file
    - Blank Audit Trail
    - Blank ProjectQuickInfo in project_quick_info.json file
    - Blank user_dwgs directory
    '''
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

    # create default project directory
    project_dir = Path(DEFAULT_PROJECTS_PATH) / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # prepare annotation styles list
    annotation_styles = [annotation_style_fire_alarm, annotation_style_branch_circuits]

    def _serialize(obj):
        # dataclasses -> dict, Paths -> str, Enums -> name, others unchanged
        if is_dataclass(obj):
            result = asdict(obj)
            for k, v in result.items():
                if hasattr(v, "name"):
                    result[k] = v.name
                elif isinstance(v, Path):
                    result[k] = str(v)
            return result
        if isinstance(obj, Path):
            return str(obj)
        if hasattr(obj, "name"):
            return obj.name
        return obj

    styles_path = project_dir / "annotation_styles.json"
    with styles_path.open("w", encoding="utf-8") as f:
        json.dump([_serialize(s) for s in annotation_styles], f, indent=2)

    # create project info and write to json
    now = int(time())
    proj_info = ProjectQuickInfo(
        project_name=project_name,
        created=now,
        last_updated=now,
        drawing_order=[s.name for s in annotation_styles],
        directory_path=project_dir,
    )
    info_path = project_dir / "project_quick_info.json"
    with info_path.open("w", encoding="utf-8") as f:
        json.dump(proj_info.to_dict(), f, indent=2)


# The below 

class Project:
    def __init__(self, project_quick_info: ProjectQuickInfo):
        self.project_quick_info = project_quick_info

all_projects_info:List[ProjectQuickInfo] = []