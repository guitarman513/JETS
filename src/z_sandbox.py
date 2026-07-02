'''

class InstantlyUpdates(BaseModel):
    __OUTPUT_CONFIG_FILE_NAME:str = "EDIT_ME_PLEASE"
    is_ready_for_auto_saving:bool = False
    def save_to_file(self):
        if self.__OUTPUT_CONFIG_FILE_NAME == "EDIT_ME_PLEASE": raise NotImplementedError(f"Someone forgot to override this baseclass attribute! {self.__OUTPUT_CONFIG_FILE_NAME=}")
        if not self.is_ready_for_auto_saving: return None
        full_json_path = self.full_project_path / self.__OUTPUT_CONFIG_FILE_NAME
        Path(full_json_path).write_text(self.model_dump_json(serialize_as_any=True, indent=4))
        return None

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        self.save_to_file()

'''


from models.z_model_hierarchy import InstantlyUpdates
from pathlib import Path

full_dir_path = Path("/Users/jmulhern/Desktop/test")

class A(InstantlyUpdates):
    full_project_path:Path = full_dir_path
    OUTPUT_CONFIG_FILE_NAME:str = 'joe.json'
    test:int = 9

    @classmethod
    def create(cls):
        return A()

aa = A.create()
aa.test=1
# a = A.model_validate_json(
#     load_path.read_text()
# )

print(aa)