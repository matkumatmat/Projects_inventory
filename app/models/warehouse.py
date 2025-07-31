# app/models/warehouse_models.py

from app.utils.extensions import db
# --- PERUBAHAN DI SINI ---
# Kita cuma butuh JSON yang universal, bukan JSONB yang spesifik
from sqlalchemy import JSON 

# --- Tabel Asosiasi (Jembatan) ---
warehouse_product_class_association = db.Table('warehouse_product_class_association',
    db.Column('warehouse_id', db.Integer, db.ForeignKey('warehouses.id'), primary_key=True),
    db.Column('product_class_id', db.Integer, db.ForeignKey('product_classes.id'), primary_key=True)
)

class Warehouse(db.Model):
    __tablename__ = 'warehouses'
    id = db.Column(db.Integer, primary_key=True)
    erp_id = db.Column(db.String(50), unique=True, nullable=False, comment="ID Gudang dari ERP")
    building_name = db.Column(db.String(255), nullable=False, comment="Nama Gedung atau Lokasi")
    
    racks = db.relationship("Rack", back_populates="warehouse", cascade="all, delete-orphan")
    allowed_product_classes = db.relationship("ProductClass", secondary=warehouse_product_class_association, backref="warehouses")

class Rack(db.Model):
    __tablename__ = 'racks'
    id = db.Column(db.Integer, primary_key=True)
    rack_identifier = db.Column(db.String(255), unique=True, nullable=False, comment="ID unik rak, misal: 107-ccell-14-AA-1")
    kolom = db.Column(db.String(50), nullable=True, index=True)
    baris = db.Column(db.String(50), nullable=True, index=True)
    
    warehouse_id = db.Column(db.Integer, db.ForeignKey('warehouses.id'), nullable=False)
    warehouse = db.relationship("Warehouse", back_populates="racks")
    
    # --- PERUBAHAN DI SINI ---
    # Ganti dari JSONB ke JSON biasa biar kompatibel sama SQLite
    properties = db.Column(JSON, nullable=True, comment="Menyimpan detail rak lain yang tidak konsisten")
    # -------------------------
    
    stock_locations = db.relationship("StockLocation", back_populates="rack")

# ... sisa model (AllocationType, Allocation, dll.) tidak perlu diubah ...
# (Kode sisanya sama persis dengan yang ada di warehouse_models_complete)

class AllocationType(db.Model):
    __tablename__ = 'allocation_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment="Contoh: reguler, tender, swt")
    allocations = db.relationship("Allocation", back_populates="allocation_type")

class Allocation(db.Model):
    __tablename__ = 'allocations'
    id = db.Column(db.Integer, primary_key=True)
    allocation_code = db.Column(db.String(100), unique=True, nullable=False, comment="Kode unik alokasi, misal: nomor kontrak")
    total_quantity = db.Column(db.Integer, nullable=False, comment="Total kuantitas untuk alokasi/kontrak ini")
    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=False)
    allocation_type_id = db.Column(db.Integer, db.ForeignKey('allocation_types.id'), nullable=False)
    product_batch = db.relationship("ProductBatch", back_populates="allocations")
    allocation_type = db.relationship("AllocationType", back_populates="allocations")
    details = db.relationship("AllocationDetail", back_populates="allocation", cascade="all, delete-orphan")

class AllocationDetail(db.Model):
    __tablename__ = 'allocation_details'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, comment="Jumlah stok untuk tujuan ini")
    destination = db.Column(db.String(255), nullable=True, comment="Nama tujuan, misal: RS A, Cabang B")
    status = db.Column(db.String(50), nullable=False, default='DITITIP', comment="Status: DITITIP, DIKIRIM, DIPROSES")
    allocation_id = db.Column(db.Integer, db.ForeignKey('allocations.id'), nullable=False)
    allocation = db.relationship("Allocation", back_populates="details")
    locations = db.relationship("StockLocation", back_populates="allocation_detail", cascade="all, delete-orphan")

class StockLocation(db.Model):
    __tablename__ = 'stock_locations'
    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False, comment="Jumlah stok di lokasi spesifik ini")
    allocation_detail_id = db.Column(db.Integer, db.ForeignKey('allocation_details.id'), nullable=False)
    rack_id = db.Column(db.Integer, db.ForeignKey('racks.id'), nullable=True, comment="NULL jika stok masih di palet")
    allocation_detail = db.relationship("AllocationDetail", back_populates="locations")
    rack = db.relationship("Rack", back_populates="stock_locations")
