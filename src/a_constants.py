from pathlib import Path

######
# Defaults that never change, and are not user-editable. Think "New Install of JETS"
# These are used to initialize the JetsConfig too.
# No imports from src allowed here. If you need to import something from src it doesn't belong here.
######
DEFAULT_JETS_DATA_DIR = Path.home() / ".jets"
DEFAULT_JETS_CONFIG_FILE = DEFAULT_JETS_DATA_DIR / "jets.json"
DEFAULT_PROJECT_BROWSER_DIR = DEFAULT_JETS_DATA_DIR / "projects" # For project browser
DEFAULT_REFERENCE_PROJECT_DIR = DEFAULT_JETS_DATA_DIR / "default_project" # For project browser
#TODO: Allow users to restore the default database if they mess it up too badly.
DEFAULT_REFERENCE_DB_DIR = DEFAULT_REFERENCE_PROJECT_DIR / "database"

# This file is src/a_constants.py
THIS_FILES_PATH = Path(__file__).parent
IMMUTABLE_DEFAULT_REFERENCE_DB_DIR = THIS_FILES_PATH / 'immutable' / 'default_database'
