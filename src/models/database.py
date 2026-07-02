from pydantic import BaseModel
from uuid import UUID
from enum import StrEnum, Enum
from typing import List, Union, Literal, Dict
from pathlib import Path

from models.z_model_hierarchy import InstantlyUpdates

class UOM(StrEnum):
    LENGTH = "LENGTH"
    COUNT = "COUNT"
    ABS = "ABS"

class UnitMultiplier(Enum):
    E = 1
    C = 10
    M = 1000

class LaborRates(BaseModel):
    labor1: float
    labor2: float
    labor3: float
    labor4: float
    labor5: float
    labor6: float


# UI Browser stuff (in flux rn)

class UILineItem(BaseModel):
    idx: int
    display_name: str
    order_on_page: float
    parent_category_idx: int | None
    line_item_type: Literal["SPACER", "CATEGORY", "ITEM", "ASSEMBLY"]


class DatabaseItem(UILineItem):
    default_uom: UOM            # the default unit of measure for this item. e.g. LENGTH or COUNT
    price_unit: UnitMultiplier  # the unit multiplier for the price. e.g. E = 1, C = 10, M = 1000. So if the price is $100.00 and the price_unit is C, then the price is actually $1.00 per unit.
    price: float                # the price per unit of the item. e.g. $100.00
    labor_unit: UnitMultiplier  # the unit multiplier for the labor. e.g. E = 1, C = 10, M = 1000. So if the labor is 100.00 hours and the labor_unit is C, then the labor is actually 1.00 hour per unit.
    labor_rates: LaborRates     # Labor rates in hours for each of the 6 labor categories. e.g. labor1 = 0.5, labor2 = 1, labor3 = 2, labor4 = 4, labor5 = 5, labor6 = 6
    last_updated: float         # Unix timestamp
    price_code: str | None = None


class AssemblyComponent(BaseModel):
    line_item_type: Literal["SPACER", "ITEM", "ASSEMBLY"]
    # Below are only important if kind == "DatabaseItem" or "DatabaseAssembly"
    source_idx: int # this is -1 if unlinked to itemdatabase
    display_name: str
    multiplier: float
    divisor: float
    uom: UOM


class DatabaseAssembly(UILineItem):
    components: list[AssemblyComponent]


# Because these items have UI information, create separate instances for item_db, assembly_db, etc.
class Database(InstantlyUpdates):
    PROJECT_PATH:Path = str("EDIT_ME_PLEASE")
    OUTPUT_CONFIG_FILE_NAME:str = 'EDIT_ME_PLEASE'
    ui_dict: Dict[int, UILineItem | DatabaseItem | DatabaseAssembly]
    
    def dbitems(self) -> List[UILineItem | DatabaseItem | DatabaseAssembly]:
        return [item for item in self.ui_dict.values() if isinstance(item, DatabaseItem)]
    def dbassemblies(self) -> List[DatabaseAssembly]:
        return [item for item in self.ui_dict.values() if isinstance(item, DatabaseAssembly)]
    def uicategories(self) -> List[UILineItem]:
        return [item for item in self.ui_dict.values() if item.line_item_type=='CATEGORY']
    def uispacers(self) -> List[UILineItem]:
        return [item for item in self.ui_dict.values() if item.line_item_type=='SPACER']
