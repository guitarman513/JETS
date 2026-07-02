# Python example to read/write this config file at ~/.jets/.jetsconfig
from pathlib import Path
import ast
import shutil
from time import time
from pydantic import BaseModel, Field
from typing import List, Tuple

from models.annotation import DEFAULT_ANNOTATION_STYLES
from models.z_model_hierarchy import InstantlyUpdates
from a_constants import *

DEFAULT_WINDOW_WIDTH = 1400
DEFAULT_WINDOW_HEIGHT = 900

class RecentPath(BaseModel):
    path: Path
    last_accessed: float = Field(default_factory=time) # Unix timestamp

class JetsConfig(InstantlyUpdates):
    OUTPUT_CONFIG_FILE_NAME: str = 'jets.json'  # required for parent class!
    PARENT_PATH: Path = DEFAULT_JETS_DATA_DIR  # required for parent class!

    reference_db_dir: Path      # path to the reference database 
    project_browser_dir: Path   # path holding all projects we want to browse

    recent_project_browser_dirs: List[RecentPath] = []
    recent_reference_db_dirs: List[RecentPath] = []

    window_width: int = DEFAULT_WINDOW_WIDTH
    window_height: int = DEFAULT_WINDOW_HEIGHT


    @classmethod
    def create_default_config(cls) -> 'JetsConfig':
        """Creates a default JetsConfig instance with default paths and settings."""
        jc = cls(
            PARENT_PATH=DEFAULT_JETS_DATA_DIR,
            reference_db_dir=DEFAULT_REFERENCE_DB_DIR,
            project_browser_dir=DEFAULT_PROJECT_BROWSER_DIR,
            recent_project_browser_dirs=[RecentPath(path=DEFAULT_PROJECT_BROWSER_DIR)],
            recent_reference_db_dirs=[RecentPath(path=DEFAULT_REFERENCE_DB_DIR)],
            window_width=DEFAULT_WINDOW_WIDTH,
            window_height=DEFAULT_WINDOW_HEIGHT,
        )
        jc.save_to_file()
        return jc

def initialize_jets_ecosystem_if_dne() -> None:
    # first check the .jets directory
    if not DEFAULT_JETS_DATA_DIR.exists(): # this is `/Users/jmulhern/.jets/` <-- store all JETS data here
        DEFAULT_JETS_DATA_DIR.mkdir(parents=False, exist_ok=True)
    # create a jets.json file too

    if not DEFAULT_JETS_CONFIG_FILE.exists(): # this is `/Users/jmulhern/.jets/jets.json` <-- store all JETS config here
        JetsConfig.create_default_config()

    # then check DEFAULT_PROJECT_BROWSER_DIR
    if not DEFAULT_PROJECT_BROWSER_DIR.exists(): # this is `/Users/jmulhern/.jets/projects/` <-- store projects here
        DEFAULT_PROJECT_BROWSER_DIR.mkdir(parents=True, exist_ok=True)
    
    # then check DEFAULT_REFERENCE_PROJECT_DIR
    if not DEFAULT_REFERENCE_PROJECT_DIR.exists(): # this is `/Users/jmulhern/.jets/projects/example_project/` <-- store the default project here
        DEFAULT_REFERENCE_PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    # The default project needs a default database, so check DEFAULT_REFERENCE_DB_DIR
    if not DEFAULT_REFERENCE_DB_DIR.exists(): # this is `/Users/jmulhern/.jets/projects/example_project/database/` <-- store the default database here
        # copy the immutable db (basic) to the default_project/ database/ dir
        shutil.copytree(IMMUTABLE_DEFAULT_REFERENCE_DB_DIR, DEFAULT_REFERENCE_DB_DIR)
    
    return None