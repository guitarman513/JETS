from uuid import uuid4, UUID
from pydantic import BaseModel
from pathlib import Path

class TakeoffFilter(BaseModel):
    filter_id: int
    filter_name: str
    filter_options: list[str]
    is_hidden: bool

DEFAULT_FILTERS:list[TakeoffFilter] = [
    TakeoffFilter(filter_id=0, filter_name="DRAWING", filter_options=[], is_hidden=False),
    TakeoffFilter(filter_id=1, filter_name="BID ITEM", filter_options=["BASE BID"], is_hidden=False),
    TakeoffFilter(filter_id=2, filter_name="SYSTEM", filter_options=[
        "DEMO",
        "FIRE ALARM",
        "BRANCH CIRCUITS",
        "LOW VOLTAGE",
    ], is_hidden=False),
    TakeoffFilter(filter_id=3, filter_name="CUSTOM FILTER 1", filter_options=["OPTION 1", "OPTION 2"], is_hidden=True),
    TakeoffFilter(filter_id=4, filter_name="CUSTOM FILTER 2", filter_options=["OPTION 1", "OPTION 2"], is_hidden=True),
    TakeoffFilter(filter_id=5, filter_name="CUSTOM FILTER 3", filter_options=["OPTION 1", "OPTION 2"], is_hidden=True),
]

class AuditEntry(BaseModel):
    time_created: float
    is_deleted:bool
    is_taken_off_of_a_dwg: bool
    annotation_id: UUID # only populated if is_taken_off_of_a_dwg
    # now for the filters associated with this entry
    drawing_id: UUID
    bid_item:str
    system:str
    #TODO: These are blank to start. Upon creation of a filter all items in audit trail will be assigned to the first option.
    custom_filter_1_selection:str
    custom_filter_2_selection:str
    custom_filter_3_selection:str

class AuditTrail(BaseModel):
    entries: list[AuditEntry] = []
    def save_to_file(self, file_path: Path):
        file_path.write_text(self.model_dump_json(indent=4))