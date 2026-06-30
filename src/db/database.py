"""
database.py — Perhaps later this will be a true SQL database.
For now, save json files. Lots of the database will include nested datastructures representing assemblies.
"""

import os
import json
import shutil
from pathlib import Path
from typing import List

from models.project import Project
from models.a_defaults import DEFAULT_PROJECTS_PATH, DEFAULT_DB_PATH


# Paste all the default db stuff in some other directory in case they get edited
def initialize_default_db():
    """Copy default database files (JSON and CSV) to the user's default database path."""
    # Create the default database directory if it doesn't exist
    DEFAULT_DB_PATH.mkdir(parents=True, exist_ok=True)
    
    # Get the defaults folder (relative to this file)
    defaults_folder = Path(__file__).parent / "defaults"
    
    # Copy all JSON and CSV files from defaults to the default database path
    for file_pattern in ["*.json", "*.csv"]:
        for file_path in defaults_folder.glob(file_pattern):
            destination = DEFAULT_DB_PATH / file_path.name
            shutil.copy2(file_path, destination)


# ── Project helpers ──────────────────────────────────────────────────────────

def get_all_projects(folder_path: str=DEFAULT_PROJECTS_PATH) -> List[Project]:
    """Get all projects by finding subdirectories in the default projects path. Projects all have an id.txt file with their project ID."""
    folder_path = Path(folder_path)
    # folder_path.mkdir(parents=True, exist_ok=True)
    
    all_projects_info:List[Project] = []
    for project_dir in sorted(folder_path.iterdir()):
        if project_dir.is_dir():
            info_file = project_dir / "project_quick_info.json"
            if info_file.exists():
                try:
                    all_projects_info.append(
                        Project(**json.load(info_file))
                        model_validate_json...
                    )
                except Exception:
                    pass  # Skip if unable to read the file
    
    return all_projects_info

