# Python example to read/write this config file at ~/.jets/.jetsconfig
from pathlib import Path
import ast
import shutil

def initialize_jets_config():
    jets_data_dir = Path.home() / '.jets'
    jets_data_dir.mkdir(parents=True, exist_ok=True)

    default_project_dir = jets_data_dir / 'default_project'
    default_project_dir.mkdir(parents=True, exist_ok=True)

    # This is where users may elect to store all of their projects. But, they can really choose any folder they like, such as on a shared network drive.
    some_projects_dir = jets_data_dir / 'projects'
    some_projects_dir.mkdir(parents=True, exist_ok=True)

    default_db_dir = jets_data_dir / 'databases' / 'default_database'
    default_db_dir.mkdir(parents=True, exist_ok=True)

    # save default project, and default database 
    premade_defaults_dir = Path(__file__).resolve().parents[2] / 'defaults'
    if premade_defaults_dir.exists() and premade_defaults_dir.is_dir():
        # add default project to .jets folder
        shutil.copytree(premade_defaults_dir / 'default_project', default_project_dir, dirs_exist_ok=False)
        # add default db to .jets/databases/default_database
        shutil.copytree(premade_defaults_dir / 'default_database', default_db_dir, dirs_exist_ok=False)
        
    # create the .jetsconfig file if it doesn't exist
    config_file_path = jets_data_dir / '.jetsconfig'
    if not config_file_path.exists() or config_file_path.read_text().strip() == '':
        config_file_path.write_text(
            f"DEFAULT_DB_DIR = {repr(str(default_db_dir))}\n"
            f"DEFAULT_PROJECT_DIR = {repr(str(some_projects_dir))}\n"
        )

    return None


def save_jets_config(default_db_dir, default_project_dir):
    jets_data_dir = Path.home() / '.jets'
    config_file_path = jets_data_dir / '.jetsconfig'
    config_file_path.write_text(
        f"DEFAULT_DB_DIR = {repr(str(default_db_dir))}\n"
        f"DEFAULT_PROJECT_DIR = {repr(str(default_project_dir))}\n"
    )


def load_jets_config_db_dir_and_project_dir() -> (Path, Path):
    jets_data_dir = Path.home() / '.jets'
    config_file_path = jets_data_dir / '.jetsconfig'
    DEFAULT_DB_DIR = ''
    DEFAULT_PROJECT_DIR = ''
    for line in config_file_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, _, value = line.partition('=')
        if key.strip() == 'DEFAULT_DB_DIR':
            DEFAULT_DB_DIR = ast.literal_eval(value.strip())
        elif key.strip() == 'DEFAULT_PROJECT_DIR':
            DEFAULT_PROJECT_DIR = ast.literal_eval(value.strip())
    return Path(DEFAULT_DB_DIR), Path(DEFAULT_PROJECT_DIR)