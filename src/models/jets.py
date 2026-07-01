# Python example to read/write this config file at ~/.jets/.jetsconfig
from pathlib import Path
import ast
import shutil
from time import time
from pydantic import BaseModel, Field
from typing import List, Tuple

from models.annotation import default_annotation_styles
######
# Defaults that never change, and are not user-editable. Think "New Install of JETS"
# These are used to initialize the JetsConfig too.
######
DEFAULT_JETS_DATA_DIR = Path.home() / ".jets"
DEFAULT_JETS_CONFIG_FILE = DEFAULT_JETS_DATA_DIR / ".jetsconfig"
DEFAULT_PROJECT_BROWSER_DIR = DEFAULT_JETS_DATA_DIR / "projects" # For project browser
DEFAULT_REFERENCE_PROJECT_DIR = DEFAULT_JETS_DATA_DIR / "default_project" # For project browser
#TODO: Allow users to restore the default database if they mess it up too badly.
DEFAULT_REFERENCE_DB_DIR = DEFAULT_REFERENCE_PROJECT_DIR / "database"
DEFAULT_ANNOTATION_STYLES = default_annotation_styles

IMMUTABLE_DEFAULT_REFERENCE_DB_DIR = Path(__file__).resolve().parents[2] / 'immutable' / 'default_database' # This is the default database that ships with JETS. It is immutable, and cannot be changed by the user. If the user messes up their database, they can restore this one.



class RecentPath(BaseModel):
    path: Path
    last_accessed: float = Field(default_factory=time) # Unix timestamp

class JetsConfig(BaseModel):
    REFERENCE_DB_DIR: Path
    PROJECT_BROWSER_DIR: Path

    RECENT_PROJECT_BROWSER_DIRS: List[RecentPath] = []
    RECENT_REFERENCE_DB_DIRS: List[RecentPath] = []

    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 900

    @classmethod
    def load(cls):
        config_file_path = Path(DEFAULT_JETS_CONFIG_FILE)
        if not config_file_path.exists() or config_file_path.read_text().strip() == '':
            raise FileNotFoundError(f"Jets config file not found at {config_file_path}.")
        return cls.model_validate_json(config_file_path.read_text())

    def save_to_file(self):
        Path(DEFAULT_JETS_CONFIG_FILE).write_text(self.model_dump_json(indent=4))

    def update(self, **kwargs): # type: ignore
        for key, value in kwargs.items(): # type: ignore
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise AttributeError(f"JetsConfig has no attribute '{key}'")
        self.save_to_file()


def initialize_dot_jets_directory():
    # Create the .jets directory and its subdirectories if they don't exist
    # See README.md for more information on the structure of the .jets directory.
    
    # Create the .jets directory if it doesn't exist
    DEFAULT_JETS_DATA_DIR.mkdir(parents=True, exist_ok=True)

    ##################################
    # Start default_project directory stuff
    # Create the default project directory if it doesn't exist
    DEFAULT_REFERENCE_PROJECT_DIR.mkdir(parents=True, exist_ok=True)

    # Create the default database directory if it doesn't exist
    if not DEFAULT_REFERENCE_DB_DIR.exists():
        # copy the default database from the immutable default database if it doesn't exist (also creates the "database" folder itself within the example_project directory)
        shutil.copytree(IMMUTABLE_DEFAULT_REFERENCE_DB_DIR, DEFAULT_REFERENCE_DB_DIR)
    # End default_project directory stuff
    ##################################

    # save a default JetsConfig file if it doesn't exist
    if not DEFAULT_JETS_CONFIG_FILE.exists() or DEFAULT_JETS_CONFIG_FILE.read_text().strip() == '':
        JetsConfig(
            REFERENCE_DB_DIR=DEFAULT_REFERENCE_DB_DIR, 
            PROJECT_BROWSER_DIR=DEFAULT_PROJECT_BROWSER_DIR,
            RECENT_PROJECT_BROWSER_DIRS = [RecentPath(path=DEFAULT_PROJECT_BROWSER_DIR)],
            RECENT_REFERENCE_DB_DIRS = [RecentPath(path=DEFAULT_REFERENCE_DB_DIR)],
            WINDOW_WIDTH=1400,
            WINDOW_HEIGHT=900,
        ).save_to_file()
   
    # Save a default annotation_styles.json file if it doesn't exist
    default_annotation_styles_path = DEFAULT_JETS_DATA_DIR / "annotation_styles.json"
    if not default_annotation_styles_path.exists():
        default_annotation_styles_path.write_text(DEFAULT_ANNOTATION_STYLES.model_dump_json(indent=4))

    return None

if __name__ == "__main__":
    initialize_dot_jets_directory()