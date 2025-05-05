
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pdf_generator import generate_payment_status_pdf
import models, schemas, database
from sqlalchemy import or_


router = APIRouter()


# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/add-transport")
def add_transport(data: schemas.TransportCompanyBase, db: Session=Depends(get_db)):
    transport = models.TransportCompany(**data.dict())
    db.add(transport)
    db.commit()
    db.refresh(transport)
    return {"message": "Transport company added", "data": transport}

@router.get("/transports")
def get_transports(db: Session = Depends(get_db)):
    transports = db.query(models.TransportCompany).all()
    return transports


@router.post("/add-item")
def add_item(data: schemas.ItemBase, db: Session=Depends(get_db)):
    item = models.Item(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return {"message": "Item added", "data": item}

@router.get("/items")
def get_items(db: Session = Depends(get_db)):
    items = db.query(models.Item).all()
    return items



@router.post("/add-unit")
def add_unit(data: schemas.QuantityUnitBase, db: Session=Depends(get_db)):
    existing = db.query(models.QuantityUnit).filter_by(quantity_unit=data.quantity_unit).first()
    if existing:
        raise HTTPException(status_code=400, detail="Unit already exists")
    unit = models.QuantityUnit(**data.dict())
    db.add(unit)
    db.commit()
    db.refresh(unit)
    return {"message": "Quantity unit added", "data": unit}

@router.get("/units")
def get_units(db: Session = Depends(get_db)):
    units = db.query(models.QuantityUnit).all()
    return units



@router.post("/add-voucher")
def add_voucher(voucher: schemas.VoucherCreate, db: Session = Depends(get_db)):
    # Check for duplicate voucher number
    existing = db.query(models.Voucher).filter_by(voucher_number=voucher.voucher_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Voucher number already exists")

    # Create and save the voucher
    new_voucher = models.Voucher(
        voucher_number=voucher.voucher_number,
        bill_date=voucher.bill_date,
        invoice_number=voucher.invoice_number,
        party_name=voucher.party_name,
        transport_id=voucher.transport_id,
        lr_number=voucher.lr_number,
        item_id=voucher.item_id,
        quantity=voucher.quantity,
        unit_id=voucher.unit_id,
        actual_weight=voucher.actual_weight,
        charged_weight=voucher.charged_weight,
        rate=voucher.rate,
        amount=voucher.amount,
        base_amount=voucher.base_amount,
        extra_charges=voucher.extra_charges,
        total_amount=voucher.total_amount,
        round_off=voucher.round_off
    )
    db.add(new_voucher)
    db.commit()
    db.refresh(new_voucher)

    for bale in voucher.bales:
        db.add(models.VoucherBale(
            voucher_id=new_voucher.id,
            voucher_number=new_voucher.voucher_number,
            invoice_number=new_voucher.invoice_number,
            bale_number=bale.bale_number,
            quantity=bale.quantity,
            status="Rejected"
        ))

    db.commit()
    return {
        "message": "Voucher and bales added successfully.",
        "data": {
            "voucher_number": new_voucher.voucher_number,
            "total_bales": len(voucher.bales)
        }
    }

@router.get("/voucher-bales")
def get_bales(
    voucher_number: str=Query(...),
    db: Session=Depends(get_db)
):
    query = db.query(models.VoucherBale).filter(models.VoucherBale.voucher_number == voucher_number)
    bales = query.all()
    return {"voucher_number": voucher_number, "count": len(bales), "bales": bales}


@router.get("/voucher-details")
def get_all_voucher_details(db: Session=Depends(get_db)):
    vouchers = db.query(models.Voucher).all()

    all_data = []

    for voucher in vouchers:
        bales = db.query(models.VoucherBale).filter(
            models.VoucherBale.voucher_number == voucher.voucher_number
        ).all()

        voucher_data = {
            "voucher_number": voucher.voucher_number,
            "bill_date": voucher.bill_date,
            "invoice_number": voucher.invoice_number,
            "party_name": voucher.party_name,
            "lr_number": voucher.lr_number,
            "quantity": voucher.quantity,
            "actual_weight": voucher.actual_weight,
            "charged_weight": voucher.charged_weight,
            "rate": voucher.rate,
            "amount": voucher.amount,
            "base_amount": voucher.base_amount,
            "extra_charges": voucher.extra_charges,
            "total_amount": voucher.total_amount,
            "round_off": voucher.round_off,
            "transport": {
                "id": voucher.transport.id,
                "name": voucher.transport.transport_name,
                "rate": voucher.transport.rate
            } if voucher.transport else None,
            "item": {
                "id": voucher.item.id,
                "name": voucher.item.item_name,
                "item_number": voucher.item.item_number
            } if voucher.item else None,
            "unit": {
                "id": voucher.unit.id,
                "name": voucher.unit.quantity_unit
            } if voucher.unit else None,
            "bales": [
                {
                    "id": bale.id,
                    "bale_number": bale.bale_number,
                    "quantity": bale.quantity,
                    "status": bale.status
                }
                for bale in bales
            ]
        }

        all_data.append(voucher_data)

    return {"count": len(all_data), "vouchers": all_data}


@router.patch("/accept-bales")
def accept_selected_bales(payload: schemas.BaleAcceptRequest, db: Session=Depends(get_db)):
    updated = 0
    for bale_number in payload.bale_numbers:
        bale = db.query(models.VoucherBale).filter(
            models.VoucherBale.voucher_number == payload.voucher_number,
            models.VoucherBale.bale_number == bale_number
        ).first()

        if bale and bale.status != "Accepted":
            bale.status = "Accepted"
            updated += 1

    db.commit()

    # Check if ALL bales are now accepted
    all_bales = db.query(models.VoucherBale).filter(
        models.VoucherBale.voucher_number == payload.voucher_number
    ).all()
    all_accepted = all(bale.status == "Accepted" for bale in all_bales)

    created_payment = None
    if all_accepted:
        voucher = db.query(models.Voucher).filter(
            models.Voucher.voucher_number == payload.voucher_number
        ).first()

        if voucher:
            tds_percent = 2.0  # Example: 2% TDS
            net_total = voucher.total_amount
            net_payable = net_total - (net_total * tds_percent / 100)

            payment = models.Payment(
    bill_no=voucher.voucher_number,
    lr_no=voucher.lr_number,
    amount=voucher.total_amount,
    tds_percent=tds_percent,
    net_total=net_total,
    net_payable=net_payable,
    payment_status="Incomplete",
    quantity=voucher.quantity,
    created_at=datetime.utcnow()
)


            db.add(payment)
            db.commit()
            db.refresh(payment)
            created_payment = payment

    return {
        "message": f"{updated} bale(s) accepted for voucher '{payload.voucher_number}'.",
        "accepted_bales": payload.bale_numbers,
        "payment_created": bool(created_payment),
        "payment_details": created_payment if created_payment else None
    }


@router.patch("/update-bale-quantity")
def update_bale_quantity(data: schemas.BaleQuantityUpdate, db: Session = Depends(get_db)):
    # Check if payment is complete
    payment = db.query(models.Payment).filter(
        models.Payment.bill_no == data.voucher_number,
        models.Payment.payment_status == "Complete"
    ).first()

    if payment:
        raise HTTPException(
            status_code=400,
            detail="❌ Cannot update. Payment already marked as 'Complete'."
        )

    # Update bale
    bale = db.query(models.VoucherBale).filter(
        models.VoucherBale.voucher_number == data.voucher_number,
        models.VoucherBale.bale_number == data.bale_number
    ).first()

    if not bale:
        raise HTTPException(status_code=404, detail="❌ Bale not found.")

    bale.quantity = data.quantity
    bale.remarks = data.remarks
    db.commit()
    db.refresh(bale)

    # Recalculate total quantity for the voucher
    all_bales = db.query(models.VoucherBale).filter(
        models.VoucherBale.voucher_number == data.voucher_number
    ).all()
    total_quantity = sum(b.quantity for b in all_bales)

    # Update Voucher
    voucher = db.query(models.Voucher).filter(
        models.Voucher.voucher_number == data.voucher_number
    ).first()

    if not voucher:
        raise HTTPException(status_code=404, detail="❌ Voucher not found.")

    voucher.quantity = total_quantity
    voucher.total_amount = total_quantity * voucher.rate
    voucher.round_off = round(voucher.total_amount) - voucher.total_amount
    voucher.net_payable = round(voucher.total_amount)
    db.commit()
    db.refresh(voucher)

    # Update Payment as well
    payment = db.query(models.Payment).filter(
        models.Payment.bill_no == data.voucher_number
    ).first()

    if payment:
        payment.quantity = total_quantity
        payment.net_total = voucher.total_amount
        payment.net_payable = voucher.net_payable
        db.commit()
        db.refresh(payment)

    return {
        "message": f"✅ Bale '{data.bale_number}' updated successfully.",
        "updated_bale": {
            "bale_number": bale.bale_number,
            "quantity": bale.quantity,
            "remarks": bale.remarks
        },
        "updated_voucher": {
            "voucher_number": voucher.voucher_number,
            "total_quantity": total_quantity,
            "total_amount": voucher.total_amount,
            "net_payable": voucher.net_payable
        },
        "updated_payment": {
            "bill_no": payment.bill_no,
            "quantity": payment.quantity,
            "net_total": payment.net_total,
            "net_payable": payment.net_payable
        }
    }

@router.get("/payments/recent")
def get_recent_payments(db: Session=Depends(get_db)):
    payments = db.query(models.Payment).order_by(
        models.Payment.created_at.desc()
    )

    return {
        "payments": [
            {
                "id": p.id,
                "bill_no": p.bill_no,
                "lr_no": p.lr_no,
                "amount": p.amount,
                "tds_percent": p.tds_percent,
                "net_total": p.net_total,
                "net_payable": p.net_payable,
                "created_at": p.created_at
            }
            for p in payments
        ]
    }


@router.post("/payments/by-lr")
def get_payments_by_lr_and_bill(
    payload: schemas.LRAndBillRequest,
    db: Session = Depends(get_db)
):
    lr_numbers = payload.lr_numbers
    bill_numbers = payload.bill_numbers

    payments = db.query(models.Payment).filter(
        or_(
            models.Payment.lr_no.in_(lr_numbers),
            models.Payment.bill_no.in_(bill_numbers)
        )
    ).all()

    return {
        "lr_numbers": lr_numbers,
        "bill_numbers": bill_numbers,
        "count": len(payments),
        "payments": [
            {
                "id": p.id,
                "bill_no": p.bill_no,
                "lr_no": p.lr_no,
                "amount": p.amount,
                "tds_percent": p.tds_percent,
                "net_total": p.net_total,
                "net_payable": p.net_payable,
                "payment_status": p.payment_status,
                "quantity": p.quantity,
                "created_at": p.created_at
            }
            for p in payments
        ]
    }

@router.patch("/payments/mark-complete")
def mark_payments_complete(
    payload: schemas.LRAndBillRequest,
    db: Session = Depends(get_db)
):
    from sqlalchemy import or_
    
    payments = db.query(models.Payment).filter(
        or_(
            models.Payment.lr_no.in_(payload.lr_numbers),
            models.Payment.bill_no.in_(payload.bill_numbers)
        )
    ).all()

    if not payments:
        raise HTTPException(status_code=404, detail="No payments found matching the criteria.")

    updated = []
    for payment in payments:
        if payment.payment_status != "Complete":
            payment.payment_status = "Complete"
            updated.append(payment.bill_no)

    db.commit()

    return {
        "updated_count": len(updated),
        "updated_bills": updated,
        "message": "Marked payments as Complete."
    }

@router.get("/payment-status")
def get_all_payment_statuses(db: Session = Depends(get_db)):
    payments = db.query(models.Payment).all()
    
    if not payments:
        raise HTTPException(status_code=404, detail="No payments found")
    
    payment_statuses = []
    
    for payment in payments:
        voucher = db.query(models.Voucher).filter(models.Voucher.voucher_number == payment.bill_no).first()
        transport_name = None
        
        if voucher and voucher.transport:
            transport_name = voucher.transport.transport_name
        
        payment_statuses.append({
            "bill_no": payment.bill_no,
            "lr_no": payment.lr_no,
            "payment_status": payment.payment_status,
            "net_payable": payment.net_payable,
            "created_at": payment.created_at,
            "transport_name": transport_name
        })
    
    return {
        "count": len(payment_statuses),
        "statuses": payment_statuses
    }


@router.post("/generate-payment-pdf")
def generate_pdf_endpoint(data: dict):
    statuses = data.get("statuses", [])
    pdf_buffer = generate_payment_status_pdf(statuses)
    return StreamingResponse(pdf_buffer, media_type="application/pdf", headers={
        "Content-Disposition": "attachment; filename=payment_status.pdf"
    })

@router.patch("/update-payment-quantity")
def update_quantity_based_on_bales(request: schemas.QuantityUpdateRequest, db: Session = Depends(get_db)):
    bale_numbers = request.bale_numbers

    # Count the number of matching bales grouped by voucher_number
    voucher_quantity_map = {}
    for bale_number in bale_numbers:
        bale = db.query(models.VoucherBale).filter(models.VoucherBale.bale_number == bale_number).first()
        if bale:
            voucher_number = bale.voucher_number
            if voucher_number in voucher_quantity_map:
                voucher_quantity_map[voucher_number] += 1
            else:
                voucher_quantity_map[voucher_number] = 1

    updated = []
    for voucher_number, qty in voucher_quantity_map.items():
        payment = db.query(models.Payment).filter(models.Payment.bill_no == voucher_number).first()
        if payment:
            payment.quantity = qty
            updated.append({"bill_no": voucher_number, "updated_quantity": qty})

    db.commit()

    return {
        "message": "Quantity updated in payment table based on bale numbers.",
        "updated": updated
    }

@router.get("/all-voucher-bales-full")
def get_all_bale_details(db: Session = Depends(get_db)):
    bales = db.query(models.VoucherBale).all()

    if not bales:
        raise HTTPException(status_code=404, detail="❌ No bales found.")

    results = []
    for bale in bales:
        results.append({
            "bale_number": bale.bale_number,
            "quantity": bale.quantity,
            "status": bale.status,
            "remarks": bale.remarks or "",
            "voucher_number": bale.voucher_number,
            "invoice_number": bale.invoice_number,
            "created_at": str(bale.created_at) if hasattr(bale, "created_at") else None
        })

    return {
        "total_bales": len(results),
        "bales": results
    }
