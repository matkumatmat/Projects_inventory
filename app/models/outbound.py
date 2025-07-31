# app/models/outbound_models.py

from app.utils.extensions import db
import datetime

class ShipmentOrder(db.Model):
    __tablename__ = 'shipment_orders'
    id = db.Column(db.Integer, primary_key=True)
    
    # --- Info Dokumen & ERP ---
    doc_ps = db.Column(db.String(100), nullable=True)
    doc_so = db.Column(db.String(100), nullable=True)
    doc_pl = db.Column(db.String(100), nullable=True)
    doc_consignment = db.Column(db.String(100), nullable=True)
    mov_code = db.Column(db.String(100), nullable=True, comment="Kode Movement dari ERP Pusat")
    
    # --- Info Konsumen & Penerusan ---
    customer_id = db.Column(db.String(100))
    customer_name = db.Column(db.String(255))
    forwarding_name = db.Column(db.String(255), nullable=True)
    forwarding_address = db.Column(db.Text, nullable=True)
    
    # --- Info Jadwal & Status ---
    planned_ship_date = db.Column(db.Date)
    actual_ship_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), default='PENDING', comment="PENDING, PACKING, READY_TO_SHIP, SHIPPED, DOCUMENTED")

    # --- Info Final ---
    merged_document_url = db.Column(db.String(512), nullable=True, comment="URL PDF gabungan dari Admin Office")

    # Relasi ke catatan pengepakannya (satu order punya satu slip pengepakan)
    packing_slip = db.relationship('PackingSlip', back_populates='shipment_order', uselist=False, cascade="all, delete-orphan")

class PackingSlip(db.Model):
    __tablename__ = 'packing_slips'
    id = db.Column(db.Integer, primary_key=True)
    reference_no = db.Column(db.String(100), unique=True, nullable=False, comment="Nomor referensi unik untuk slip ini")
    
    packer_code = db.Column(db.String(100), nullable=True)
    checker_staff = db.Column(db.String(100), nullable=True)

    shipment_order_id = db.Column(db.Integer, db.ForeignKey('shipment_orders.id'), unique=True)
    shipment_order = db.relationship('ShipmentOrder', back_populates='packing_slip')

    # Relasi ke box-box yang dipak
    packed_boxes = db.relationship('PackedBox', back_populates='packing_slip', cascade="all, delete-orphan")

class PackedBox(db.Model):
    __tablename__ = 'packed_boxes'
    id = db.Column(db.Integer, primary_key=True)
    box_number = db.Column(db.Integer, nullable=False)
    weight_kg = db.Column(db.Float, nullable=True)
    
    packing_slip_id = db.Column(db.Integer, db.ForeignKey('packing_slips.id'))
    packing_slip = db.relationship('PackingSlip', back_populates='packed_boxes')

    # Relasi ke item-item di dalam box ini
    packed_items = db.relationship('PackedItem', back_populates='packed_box', cascade="all, delete-orphan")

class PackedItem(db.Model):
    __tablename__ = 'packed_items'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, comment="Jumlah yang dimasukkan ke dalam box ini")

    packed_box_id = db.Column(db.Integer, db.ForeignKey('packed_boxes.id'))
    
    # --- Kunci Utama: Asal-usul Barang ---
    # Menunjukkan barang ini diambil dari rak/palet mana
    stock_location_id = db.Column(db.Integer, db.ForeignKey('stock_locations.id'))
    
    packed_box = db.relationship('PackedBox', back_populates='packed_items')
    stock_location = db.relationship('StockLocation') # Untuk tau asal rak & kuantitasnya
