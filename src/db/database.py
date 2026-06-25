"""
database.py — Perhaps later this will be a true SQL database.
For now, save json files. Lots of the database will include nested datastructures representing assemblies.
"""

import os
import json
import shutil
from pathlib import Path


DEFAULT_DB_PATH = Path.home() / ".jets" / "_default_database" 
DEFAULT_PROJECTS_PATH = Path.home() / ".jets" / "_default_projects" 


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

def get_all_projects(folder_path: str=DEFAULT_PROJECTS_PATH):
    """Get all projects by finding subdirectories in the default projects path. Projects all have an id.txt file with their project ID."""
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    project_ids = []
    for project_dir in sorted(folder_path.iterdir()):
        if project_dir.is_dir():
            id_file = project_dir / "id.txt"
            if id_file.exists():
                try:
                    project_id = id_file.read_text().strip()
                    project_ids.append(project_id)
                except Exception:
                    pass  # Skip if unable to read the file
    
    return project_ids




def create_project(name: str, folder_path: str=DEFAULT_PROJECTS_PATH) -> str:
    """Create a new project directory with an id.txt file and return its ID."""
    folder_path = Path(folder_path)
    project_path = folder_path / name
    project_path.mkdir(parents=True, exist_ok=True)
    
    # Generate a project ID (using folder name with timestamp)
    from datetime import datetime
    project_id = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Write project ID to id.txt
    id_file = project_path / "id.txt"
    id_file.write_text(project_id)
    
    return project_id



def get_project(project_id: str, folder_path: str=DEFAULT_PROJECTS_PATH) -> Path:
    """Find and return the path to a project by its ID."""
    folder_path = Path(folder_path)
    folder_path.mkdir(parents=True, exist_ok=True)
    
    for project_dir in folder_path.iterdir():
        if project_dir.is_dir():
            id_file = project_dir / "id.txt"
            if id_file.exists():
                try:
                    stored_id = id_file.read_text().strip()
                    if stored_id == project_id:
                        return project_dir
                except Exception:
                    pass
    
    return None  # Project not found

def get_drawings_for_project(project_id: str, folder_path: str=DEFAULT_PROJECTS_PATH):
    """Get all drawings for a project by its ID."""
    project_dir = get_project(project_id, folder_path)
    if not project_dir:
        return []

    drawings = []
    for drawing_file in project_dir.glob("*.pdf"):
        drawings.append({
            "filename": drawing_file.name,
            "display_name": drawing_file.stem
        })
    return drawings