# app/models/shipment_and_packing.py
from .outbound import PackingSlip # Import model PackingSlip dari outbound
from app.utils.extensions import db

class Shipment(db.Model):
    """Tabel 'Merge' atau 'Titik Temu' untuk semua pengiriman harian."""
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    
    # Dokumen Final untuk Rekonsiliasi
    ship_date = db.Column(db.Date, index=True, nullable=False)
    doc_ps = db.Column(db.String(100), nullable=True) # Packing Slip
    doc_pl = db.Column(db.String(100), nullable=True) # Picking List
    doc_do = db.Column(db.String(100), nullable=True) # Delivery Order
    doc_so = db.Column(db.String(100), nullable=True) # Sales Order
    doc_consignment = db.Column(db.String(100), nullable=True)
    erp_movement_code = db.Column(db.String(100), nullable=True)
    contract_no = db.Column(db.String(100), nullable=True)
    
    customer_id = db.Column(db.String(100), nullable=False)
    forwarding_name = db.Column(db.String(255), nullable=True)
    forwarding_address = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(50), default='PENDING_DOCUMENTATION', nullable=False)

    # Kolom Polimorfik untuk Histori Universal
    shipment_type = db.Column(db.String(50), nullable=False, index=True, comment="e.g., REGULER, TENDER, CONSIGNMENT")
    reference_id = db.Column(db.Integer, nullable=False, index=True, comment="ID dari shipment_orders, tender_items, atau consignments")
