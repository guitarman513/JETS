from typing import List, Dict, Any
from time import time
from pathlib import Path
import json
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from models.annotation import AnnotationStyle, AnnotationShape, AnnotationLineStyle, Annotation, default_annotation_styles
from models.a_defaults import DEFAULT_PROJECTS_PATH, DEFAULT_ANNOTATION_STYLES

# Reading and writing models to json files:
# project = Project.model_validate_json(
#     Path("project.json").read_text()
# )

# Path("project.json").write_text(
#     project.model_dump_json(indent=4)
# )



class Drawing(BaseModel):
    drawing_id: UUID = Field(default_factory=uuid4)
    drawing_name: str
    pdf_filename: str
    annotations: list[Annotation] = Field(default_factory=list)
    class Config:
        use_enum_values = True
    
def get_all_drawings_in_project(project: Project) -> list[Drawing]:
    drawing_directory = project.directory_path / "drawings"
    drawings: list[Drawing] = []

    if not drawing_directory.exists():
        return drawings

    for drawing_folder in drawing_directory.iterdir():
        if not drawing_folder.is_dir():
            continue
        try:
            UUID(drawing_folder.name)
        except ValueError:
            continue

        drawing_info_path = drawing_folder / "drawing.json"
        if drawing_info_path.exists():
            drawings.append(
                Drawing.model_validate_json(drawing_info_path.read_text(encoding="utf-8"))
            )

    return drawings


class Project(BaseModel):
    project_name: str
    created: int
    last_updated: int
    drawing_order: list[UUID]
    directory_path: Path
    class Config:
        json_encoders = {Path: str}

    def setup_project_as_new(self):
        # Create project dir
        self.project.directory_path.mkdir(parents=True, exist_ok=True)

        # Save a project.json file
        Path(self.project.directory_path / "project.json").write_text(
            self.project.model_dump_json(indent=4)
        )

        # Create the drawings directory
        if not Path(self.project.directory_path / "drawings").exists():
            Path(self.project.directory_path / "drawings").mkdir()

        # Create the annotation_styles.json file
        # TODO: really should load this from the default_annotation_styles.json file that users may edit found in the .jets user data directory..
        Path(self.project.directory_path / "annotation_styles.json").write_text(
            json.dumps([style.model_dump() for style in default_annotation_styles], indent=2)
        )

# Maybe should implement methods in `Project` to do things like get drawings etc. But maybe not. Prob utility in having a container to hold things like drawing thumbnails and stuff
# I suppose this should be able to hold larger things like the pdf drawings. Maybe should fully load only the active one at a time, and 
# Always make sure to save each annotation to the folder every time it is updated
class ProjectManager:
    def __init__(self, project: Project):
        self.project = project
        # self.drawings_dict: dict[UUID, Drawing] = {load from project folder}
        # self.styles: List[AnnotationStyle] = {load from project folder}
        

    






#TODO: EDIT BELOW 
def create_default_project(project_name:str = "default_project"):
    '''
    Create:
    - Project directory in defaults/default_project
    - Default AnnotationStyle objects in annotation_styles.json file
    - Blank Audit Trail
    - Blank Project in project.json file
    - Blank user_dwgs directory
    '''
    

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
    proj_info = Project(
        project_name=project_name,
        created=now,
        last_updated=now,
        drawing_order=[s.name for s in annotation_styles],
        directory_path=project_dir,
    )
    info_path = project_dir / "project_quick_info.json"
    with info_path.open("w", encoding="utf-8") as f:
        json.dump(proj_info.to_dict(), f, indent=2)

