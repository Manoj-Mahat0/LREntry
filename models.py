from sqlalchemy import Column, DateTime, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class TransportCompany(Base):
    __tablename__ = "transport_companies"
    id = Column(Integer, primary_key=True)
    transport_name = Column(String(100))
    address = Column(String(200))
    contact = Column(String(50))
    rate = Column(Float)

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    item_number = Column(String(50))
    item_name = Column(String(100))
    quantity = Column(Integer)

class QuantityUnit(Base):
    __tablename__ = "quantity_units"
    id = Column(Integer, primary_key=True)
    quantity_unit = Column(String(50), unique=True)

class Voucher(Base):
    __tablename__ = "vouchers"
    id = Column(Integer, primary_key=True)
    voucher_number = Column(String, unique=True, index=True, nullable=False)
    bill_date = Column(Date)
    invoice_number = Column(String, unique=True, index=True, nullable=False)
    party_name = Column(String(100))
    transport_id = Column(Integer, ForeignKey("transport_companies.id"))
    lr_number = Column(String(50))
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
    bill_no = Column(String(50))
    lr_no = Column(String(50))
    amount = Column(Float)
    tds_percent = Column(Float)
    net_total = Column(Float)
    net_payable = Column(Float)
    payment_status = Column(String(20), default="Incomplete")
    created_at = Column(DateTime, default=datetime.utcnow)
    quantity = Column(Integer)

class VoucherBale(Base):
    __tablename__ = "voucher_bales"
    id = Column(Integer, primary_key=True)
    voucher_id = Column(Integer, ForeignKey("vouchers.id"))
    voucher_number = Column(String(50))
    invoice_number = Column(String(50))
    bale_number = Column(String(50))
    remarks = Column(String(100), default="Normal")
    status = Column(String(20), default="Rejected")
    quantity = Column(Float, default=0)

    voucher = relationship("Voucher", back_populates="bales")
