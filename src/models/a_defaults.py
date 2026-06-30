from pathlib import Path
from typing import List
from models.annotation import default_annotation_styles


#TODO: This whole file is an override for development purposes. really this should already be set in models/jets.py
DEFAULT_DB_DIR =       Path.home() / "git" / "JETS" / "databases" / "joedb-2026-06"
DEFAULT_PROJECTS_DIR = Path.home() / "git" / "JETS" / "project_folder"

# Things for setting up new projects
DEFAULT_ANNOTATION_STYLES = default_annotation_styles