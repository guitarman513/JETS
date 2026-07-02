import re 
from pathlib import Path
import shutil
from a_constants import *

def clean_str_for_use_in_pathname(s:str) ->  str:
    lowered = s.lower()
    no_hyphens = lowered.replace('-', '_')
    alphanum_w_underscore = re.sub(r'[^a-z0-9_]+', '_', no_hyphens)
    # 4. Clean up any resulting double underscores and trim the edges
    final = re.sub(r'_+', '_', alphanum_w_underscore).strip('_')
    return final

def is_valid_path(path_obj: Path) -> bool:
    try:
        # strict=False resolves the path format against your OS syntax rules 
        # without checking if the folder actually exists yet
        path_obj.resolve(strict=False)
        return True
    except (OSError, ValueError):
        return False
