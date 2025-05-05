from datetime import date
from typing import List
from pydantic import BaseModel

class TransportCompanyBase(BaseModel):
    transport_name: str
    address: str
    contact: str
    rate: float

class ItemBase(BaseModel):
    item_number: str
    item_name: str
    quantity: int

class QuantityUnitBase(BaseModel):
    quantity_unit: str

class VoucherBaleCreate(BaseModel):
    bale_number: str

class BaleInput(BaseModel):
    bale_number: str
    quantity: float

class VoucherCreate(BaseModel):
    voucher_number: str
    bill_date: date
    invoice_number: str
    party_name: str
    transport_id: int
    lr_number: str
    item_id: int
    quantity: float
    unit_id: int
    actual_weight: float
    charged_weight: float
    rate: float
    amount: float
    base_amount: float
    extra_charges: float
    total_amount: float
    round_off: float
    bales: List[BaleInput]  # ✅ updated to accept bale_number + quantity


class BaleAcceptRequest(BaseModel):
    voucher_number: str
    bale_numbers: List[str]  # List of bale numbers to accept

class BaleQuantityUpdate(BaseModel):
    voucher_number: str
    bale_number: str
    quantity: float
    remarks: str  # e.g. "Excess Quantity", "Less Quantity", "Normal"

class QuantityUpdateRequest(BaseModel):
    bale_numbers: List[str]  # list of bale numbers

class LRAndBillRequest(BaseModel):
    lr_numbers: List[str]
    bill_numbers: List[str]

