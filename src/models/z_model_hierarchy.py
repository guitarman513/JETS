from typing import List, Dict, Any, Literal
from time import time
from pathlib import Path
import json
from uuid import UUID, uuid4
import re

from pydantic import BaseModel, Field, computed_field


from a_utils import clean_str_for_use_in_pathname, is_valid_path

# Reading and writing models to json files:
# project = Project.model_validate_json(
#     Path("project.json").read_text()
# )

# Path("project.json").write_text(
#     project.model_dump_json(serialize_as_any=True, indent=4)
# )

class InstantlyUpdates(BaseModel):
    OUTPUT_CONFIG_FILE_NAME:str = "EDIT_ME_PLEASE"
    PARENT_PATH:Path = str("EDIT_ME_PLEASE") # could be project dir if project.json, or drawing dir if annotations.json
    # is_ready_for_auto_saving:bool = False # NOTE: Seems like I was overthinking this.
    def save_to_file(self):
        if self.OUTPUT_CONFIG_FILE_NAME == "EDIT_ME_PLEASE": raise NotImplementedError(f"Someone forgot to override this baseclass attribute! {self.OUTPUT_CONFIG_FILE_NAME=}")
        if self.PARENT_PATH == "EDIT_ME_PLEASE": raise NotImplementedError(f"Someone forgot to override this baseclass attribute! {self.PARENT_PATH=}")
        # if not self.is_ready_for_auto_saving: return None # NOTE: Seems like I was overthinking this.
        full_json_path = self.PARENT_PATH / self.OUTPUT_CONFIG_FILE_NAME
        Path(full_json_path).write_text(self.model_dump_json(serialize_as_any=True, indent=4))
        return None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save_to_file()
    
    @classmethod
    def load(cls, full_json_path:Path):
        if not full_json_path.exists() or full_json_path.read_text().strip() == '':
            raise FileNotFoundError(f"Config file not found at {full_json_path}.")
        return cls.model_validate_json(full_json_path.read_text())
