# JETS
Joe's Electrical Takeoff Software

* Running 
Need a virtual environment for development. If you don't have a .venv folder, create one with
* `python3 -m venv .venv`
* `source .venv/bin/activate`
* Then you can pip install the requirements from the pyproject.toml file with
* `pip install -e .` (need that last period '.')




# JETS HIERARCHY NOTES
* PROJECT_BROWSER_DIR may direct project browser to a dir other than `$HOME/.jets/projects` if desired
* REFERENCE_DB_DIR may be something other than `$HOME/.jets/projects/aaa_default_project/database` if desired. Recall that upon creation of a new project, its database will live INSIDE the project folder, so it may always be able to be referenced!!! The new project's database will be initialized as a COPY of the database found in DEFAULT_DB_DIR.

```
$HOME/.jets/
├─ .jets_config # REFERENCE_DB_DIR, [RECENT_PROJECT_BROWSER_DIRS], WINDOW_WIDTH, ...
|
├─ default_project/
│  ├─ annotation_styles.json     # for feeders, fire alarm, demo, etc.
│  |
│  ├─ database/
│  |  ├─ ...default database files...
│  │
├─ projects/
│  |
│  ├─ NG123_JOHNSON_ELEMENTARY/
│  │  ├─ project.json               # last_updated, drawing_order, ...
│  │  ├─ annotation_styles.json     # initially copied from aaa_default_project/
│  │  |
│  │  ├─ drawings/
│  │  │  ├─ uuid1/
│  │  │  │  ├─ drawing.json         # filename, scale, ...
│  │  │  │  ├─ annotations.json     # all markups and takeoff details
│  │  │  ├─ uuid2/...
│  │  │  ├─ uuid3/...
│  │  |
│  │  ├─ database/                  # copied from aaa_default_project/
│  │  │  ├─ ...project-specific database files...
│  │
│  ├─ ... another project ...

```



`$HOME/.jets` is the `DEFAULT_JETS_DATA_DIR`. There are config files here.
* `.jets_config`: 
```
class JetsConfig(BaseModel):
    DEFAULT_DB_DIR: Path
    DEFAULT_PROJECT_DIR: Path

    RECENT_PROJECTS: List[RecentPath] = []
    RECENT_DATABASES: List[RecentPath] = []

    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 900
```






# DEVELOPMENT NOTES/ISSUES
* I chose to include two identifiers for items and assemblies. TBD if that was a good decision. It was a development-driven decision so I don't need to memorize a bunch of numbers. 
* BUT it has the unfortunate side effect that I now have to keep track of two things that should both independently be unique. And if either of these change, they are both used in many other spots in the database. Also if a user renames a uid there could be confusion. IDK I may just abandon all references to it. But for now it is useful for sanity-checking
* EXAMPLE `"assembly_idx": 9, "assembly_name_uid": "emt_3/4_with_couplings"`
* It is entirely possible for an assembly to be in the json file, but a subassembly of itself to not be in the json file anywhere. I don't even think this would break anything as long as the subassembly is well-defined in the csv file.