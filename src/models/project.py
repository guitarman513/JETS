import shutil
from typing import List, Dict, Any, Literal
from time import time
from pathlib import Path
import json
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field, computed_field

from models.annotation import Drawing, Annotation, DEFAULT_ANNOTATION_STYLES, AnnotationStyles
from models.audit_trail import AuditTrail
from models.jets import initialize_jets_ecosystem_if_dne, RecentPath

from a_utils import clean_str_for_use_in_pathname, is_valid_path
from a_constants import *
from models.z_model_hierarchy import InstantlyUpdates


class ProjectInfo(InstantlyUpdates):
    """A small class for fast, top-level project information
    # NOTE: Unless loading this for a quick look at project data, this should be created with the classmethod via ProjectManager which will instantiate other default dirs and configs a real project needs.
    """
    PARENT_PATH:Path = str("EDIT_ME_PLEASE")
    OUTPUT_CONFIG_FILE_NAME:str = 'project.json'    # required for parent class! 
    project_name: str        # This can hAVe WEIrd cAsE and Symb0l$ unlike full_project_path
    created: int             # Unix timestamp
    last_updated: int
    drawing_order: list[UUID]# Even though this class shouldn't have deep knowledge of drawings, it may be nice to know if there are any drawings at all, which you can do by counting this list's elements
    # NOTE: Always validate this elsewhere!
    full_project_path: Path  # such as $HOME/.jets/projects/<THIS_PROJECT>

def get_projects_infos(parent_path:Path) -> List[ProjectInfo]:
    projs_infos:List[ProjectInfo] = []
    for path_obj in parent_path.iterdir():
        if path_obj.is_dir() and (path_obj / "project.json").exists():
            # then we have a valid project dir boys!!
            pi = ProjectInfo.load(path_obj / "project.json")
            projs_infos.append(pi)
    return sort_projects_infos(projs_infos)

sort_options = Literal["name_asc", "name_desc", "created_asc", "created_desc", "last_updated_asc", "last_updated_desc"]
def sort_projects_infos(projs_infos:List[ProjectInfo], by: sort_options = "created_asc") -> List[ProjectInfo]:
    if by == "name_asc":
        return sorted(projs_infos, key=lambda p: p.project_name.lower())
    elif by == "name_desc":
        return sorted(projs_infos, key=lambda p: p.project_name.lower(), reverse=True)
    elif by == "created_asc":
        return sorted(projs_infos, key=lambda p: p.created)
    elif by == "created_desc":
        return sorted(projs_infos, key=lambda p: p.created, reverse=True)
    elif by == "last_updated_asc":
        return sorted(projs_infos, key=lambda p: p.last_updated)
    elif by == "last_updated_desc":
        return sorted(projs_infos, key=lambda p: p.last_updated, reverse=True)
    else:
        raise ValueError(f"Invalid sort option: {by}")


# The big kahuna
class ProjectManager:
    def __init__(
            self, 
            project_info:ProjectInfo,
            drawing_thumbnails_plain:list,
            drawing_thumbnails_annotated:list,
            active_drawing:Drawing | None,
            annotation_styles:AnnotationStyles,
            audit_trail:AuditTrail,
        ):
        self.project_info:ProjectInfo = project_info
        self.drawing_thumbnails_plain:list = drawing_thumbnails_plain
        self.drawing_thumbnails_annotated:list = drawing_thumbnails_annotated
        self.active_drawing:Drawing | None = active_drawing
        self.annotation_styles:AnnotationStyles = annotation_styles
        self.audit_trail:AuditTrail = audit_trail

    @classmethod
    def create_new_project(
            cls,
            project_name:str,
            parent_dir_to_store_this_project:Path,
        ):
        initialize_jets_ecosystem_if_dne() 
        '''
        projs/            <--- assumed to be valid now
        - this_project/   <--- *** see if we can create this ***
        '''
        # Check if we can create this project's path
        proj_name_clean = clean_str_for_use_in_pathname(project_name)
        full_proj_path = parent_dir_to_store_this_project / proj_name_clean
        if not is_valid_path(full_proj_path): raise ValueError(f"\nNot a valid path: {full_proj_path}\n")

        # Create default boilerplate (see README.md for tree)
        project_info = ProjectInfo(
            OUTPUT_CONFIG_FILE_NAME='project.json',
            PARENT_PATH=full_proj_path,
            project_name=project_name,
            created=time(),
            last_updated=time(),
            drawing_order=[],
            full_project_path=full_proj_path
        )
        project_info.last_updated = time() # triggers a config file save since invoking __set_attr__ (see InstantlyUpdates class defn)
        '''
        projs/            
        - this_project/     # :)
            - project.json  # :)
            - annotation_styles.json  # *** create this ***
            - audit_trail.json  # *** create this ***
            - drawings/         # *** create this (will be blank cause no dwgs yet) ***
            - database/         # *** create this with default db data ***
        '''
        annotation_styles = AnnotationStyles(OUTPUT_CONFIG_FILE_NAME='annotation_styles.json', PARENT_PATH=full_proj_path)
        annotation_styles.annotation_styles = DEFAULT_ANNOTATION_STYLES # should trigger config file save

        audit_trail = AuditTrail(PARENT_PATH=full_proj_path, OUTPUT_CONFIG_FILE_NAME='audit_trail.json')
        audit_trail.entries = [] # should trigger congif file 
        
        Path(full_proj_path / "drawings").mkdir(exist_ok=False, parents=False)

        # now copy default db stuff into the new project's database dir (not the immutable one that's source controlled! This is from the .jets reference dir)
        Path(full_proj_path / "database").mkdir(exist_ok=False, parents=False) # create this new project's one now
        shutil.copytree(DEFAULT_REFERENCE_DB_DIR, full_proj_path / "database", dirs_exist_ok=True)

        # any other setup
        return ProjectManager(
            project_info=project_info,
            drawing_thumbnails_plain=[],
            drawing_thumbnails_annotated=[],
            active_drawing=None,
            annotation_styles=annotation_styles,
            audit_trail=audit_trail
        )
        



