# JETS
Joe's Electrical Takeoff Software

* Running 
Need a virtual environment for development. If you don't have a .venv folder, create one with
* `python3 -m venv .venv`
* `source .venv/bin/activate`
* Then you can pip install the requirements from the pyproject.toml file with
* `pip install -e .` (need that last period '.')


# DEVELOPMENT NOTES/ISSUES
* I chose to include two identifiers for items and assemblies. TBD if that was a good decision. It was a development-driven decision so I don't need to memorize a bunch of numbers. 
* BUT it has the unfortunate side effect that I now have to keep track of two things that should both independently be unique. And if either of these change, they are both used in many other spots in the database. Also if a user renames a uid there could be confusion. IDK I may just abandon all references to it. But for now it is useful for sanity-checking
* EXAMPLE `"assembly_idx": 9, "assembly_name_uid": "emt_3/4_with_couplings"`
* It is entirely possible for an assembly to be in the json file, but a subassembly of itself to not be in the json file anywhere. I don't even think this would break anything as long as the subassembly is well-defined in the csv file.