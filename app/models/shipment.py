# app/models/shipment_and_packing.py
from ..extensions import db

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
    
    status = db.Column(db.String(50), default='PENDING_PACKING', nullable=False)

    packing_slips = db.relationship('PackingSlip', back_populates='shipment', cascade="all, delete-orphan")

class PackingSlip(db.Model):
    """Catatan hasil proses packing fisik."""
    __tablename__ = 'packing_slips'
    id = db.Column(db.Integer, primary_key=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'), nullable=False)
    
    shipment = db.relationship("Shipment", back_populates="packing_slips")
    packed_boxes = db.relationship('PackedBox', back_populates='packing_slip', cascade="all, delete-orphan")

class PackedBox(db.Model):
    """Box fisik hasil packing."""
    __tablename__ = 'packed_boxes'
    id = db.Column(db.Integer, primary_key=True)
    box_number = db.Column(db.Integer, nullable=False)
    packing_slip_id = db.Column(db.Integer, db.ForeignKey('packing_slips.id'), nullable=False)
    
    packing_slip = db.relationship('PackingSlip', back_populates='packed_boxes')
    packed_items = db.relationship('PackedItem', back_populates='packed_box', cascade="all, delete-orphan")

class PackedItem(db.Model):
    """Item spesifik yang dimasukkan ke dalam box."""
    __tablename__ = 'packed_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    packed_box_id = db.Column(db.Integer, db.ForeignKey('packed_boxes.id'), nullable=False)
    
    # Menunjuk ke LOKASI FISIK mana barang ini diambil
    stock_location_id = db.Column(db.Integer, db.ForeignKey('stock_locations.id'), nullable=False)
    
    packed_box = db.relationship('PackedBox', back_populates='packed_items')
    stock_location = db.relationship('StockLocation')
