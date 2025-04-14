from sqlalchemy import Column, DateTime, Integer, String, Float, Date, ForeignKey, func
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class TransportCompany(Base):
    __tablename__ = "transport_companies"
    id = Column(Integer, primary_key=True)
    transport_name = Column(String)
    address = Column(String)
    contact = Column(String)
    rate = Column(Float)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    item_number = Column(String)
    item_name = Column(String)
    quantity = Column(Integer)

class QuantityUnit(Base):
    __tablename__ = "quantity_units"
    id = Column(Integer, primary_key=True)
    quantity_unit = Column(String, unique=True)

class Voucher(Base):
    __tablename__ = "vouchers"
    id = Column(Integer, primary_key=True)
    voucher_number = Column(String)
    bill_date = Column(Date)
    invoice_number = Column(String)
    party_name = Column(String)
    transport_id = Column(Integer, ForeignKey("transport_companies.id"))
    lr_number = Column(String)
    item_id = Column(Integer, ForeignKey("items.id"))
    quantity = Column(Float)
    unit_id = Column(Integer, ForeignKey("quantity_units.id"))
    actual_weight = Column(Float)
    charged_weight = Column(Float)
    rate = Column(Float)
    amount = Column(Float)
    base_amount = Column(Float)
    extra_charges = Column(Float)
    total_amount = Column(Float)
    round_off = Column(Float)

    transport = relationship("TransportCompany")
    item = relationship("Item")
    unit = relationship("QuantityUnit")
    bales = relationship("VoucherBale", back_populates="voucher")



class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    bill_no = Column(String)
    lr_no = Column(String)
    amount = Column(Float)
    tds_percent = Column(Float)
    net_total = Column(Float)
    net_payable = Column(Float)
    payment_status = Column(String, default="Incomplete")
    created_at = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Integer)  # <-- NEW FIELD



class VoucherBale(Base):
    __tablename__ = "voucher_bales"
    id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"))
    voucher_number = Column(String)
    invoice_number = Column(String)
    bale_number = Column(String)
    status = Column(String, default="Rejected")
    quantity = Column(Float, default=0)  # ✅ New field

    voucher = relationship("Voucher", back_populates="bales")
