# app/models/warehouse.py
from ..extensions import db

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    erp_id = db.Column(db.String(50), unique=True, nullable=False)
    building_name = db.Column(db.String(255), nullable=False)
    racks = db.relationship("Rack", back_populates="warehouse", cascade="all, delete-orphan")

class Rack(db.Model):
    __tablename__ = 'racks'
    id = db.Column(db.Integer, primary_key=True)
    rack_code = db.Column(db.String(50), nullable=False, comment="e.g., AA, BB, CC")
    column_no = db.Column(db.String(50), nullable=False, comment="e.g., 1, 2, 3-8")
    row_no = db.Column(db.String(50), nullable=False, comment="e.g., 1, 2, 3")
    rack_identifier = db.Column(db.String(255), unique=True, nullable=False, comment="warehouse_id-rack-kolom-baris")
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    
    warehouse = db.relationship("Warehouse", back_populates="racks")
    stock_locations = db.relationship("StockLocation", back_populates="rack")

class StockLocation(db.Model):
    """'Buku Kas Fisik'. Sumber kebenaran stok di gudang."""
    __tablename__ = 'stock_locations'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=False)
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id'), nullable=True, comment="NULL jika di palet")
    
    # --- KUNCI ATURAN RAK ---
    # Mencatat untuk alokasi apa stok ini. Format: 'TENDER-CONTRACT123' atau 'REGULER'
    allocation_identity = db.Column(db.String(255), default='REGULER', nullable=False)

    product_batch = db.relationship("ProductBatch")
    rack = db.relationship("Rack", back_populates="stock_locations")
