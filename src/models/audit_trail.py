from dataclasses import dataclass
from uuid import uuid4

DEFAULT_FILTERS = [
    (0, "DRAWING", []),
    (1, "BID ITEM", ["BASE BID"]),

    (2, "SYSTEM", [ #TODO: These systems influence the default AnnotationStyle for each audit item. For now, there must an AnnotationStyle with the same name otherwise a pop up will prompt the user to make one.
        "DEMO",
        "FIRE ALARM",
        "BRANCH CIRCUITS",
        "LOW VOLTAGE",
    ]),

    (3, "CUSTOM FILTER 1", ["OPTION 1"])
]

ID_OF_FIRST_CUSTOM_FILTER = 3
MAX_CUSTOM_FILTERS = 3

@dataclass
class AuditEntry:
    timestamp: float
    is_deleted:bool
    is_taken_off_of_a_dwg: bool
    annotation_id: uuid4 # only populated if is_taken_off_of_a_dwg
    # now for the filters associated with this entry
    drawing_id: uuid4
    system:str
    #TODO: These are blank to start. Upon creation of a filter all items in audit trail will be assigned to the first option.
    custom_filter_1_selection:str
    custom_filter_2_selection:str
    custom_filter_3_selection:str

