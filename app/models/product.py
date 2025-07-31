# app/models/product_models.py

from app.utils.extensions import db
import datetime

class ProductClass(db.Model):
    __tablename__ = 'product_classes'
    
    id = db.Column(db.Integer, primary_key=True)
    erp_id = db.Column(db.String(50), unique=True, nullable=False)
    class_name = db.Column(db.String(100))

    # Relasi balik dari warehouse_models
    # backref 'warehouses' akan dibuat secara otomatis oleh SQLAlchemy

class Product(db.Model):
    __tablename__ = 'products'

    id = db.Column(db.Integer, primary_key=True)
    erp_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255))
    manufacturer = db.Column(db.String(255))
    
    product_class_id = db.Column(db.Integer, db.ForeignKey('product_classes.id'))

    product_class = db.relationship("ProductClass", backref="products")
    batches = db.relationship("ProductBatch", back_populates="product", cascade="all, delete-orphan")
    prices = db.relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")

class ProductBatch(db.Model):
    __tablename__ = 'product_batches'

    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(100), unique=True, nullable=False)
    expiry_date = db.Column(db.Date)
    manufacturing_date = db.Column(db.Date)
    inbound_qty = db.Column(db.Integer, default=0)
    outbound_qty = db.Column(db.Integer, default=0)
    actual_stock = db.Column(db.Integer, default=0)

    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    
    product = db.relationship("Product", back_populates="batches")
    details = db.relationship("ProductDetail", back_populates="batch", uselist=False, cascade="all, delete-orphan")
    docs = db.relationship("ProductDoc", back_populates="batch", uselist=False, cascade="all, delete-orphan")
    
    # Relasi ke Allocation dari warehouse_models
    allocations = db.relationship("Allocation", back_populates="product_batch", cascade="all, delete-orphan")

class ProductDetail(db.Model):
    __tablename__ = 'product_details'

    id = db.Column(db.Integer, primary_key=True)
    nie = db.Column(db.String(100))
    length = db.Column(db.Float, nullable=True)
    width = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    
    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), unique=True)
    batch = db.relationship("ProductBatch", back_populates="details")

class ProductDoc(db.Model):
    __tablename__ = 'product_docs'

    id = db.Column(db.Integer, primary_key=True)
    front_url = db.Column(db.String(255), nullable=True)
    right_url = db.Column(db.String(255), nullable=True)
    left_url = db.Column(db.String(255), nullable=True)
    back_url = db.Column(db.String(255), nullable=True)
    group_url = db.Column(db.String(255), nullable=True)
    leaflet_url = db.Column(db.String(255), nullable=True)

    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), unique=True)
    batch = db.relationship("ProductBatch", back_populates="docs")

class ProductPrice(db.Model):
    __tablename__ = 'product_prices'

    id = db.Column(db.Integer, primary_key=True)
    het = db.Column(db.Float)
    hna = db.Column(db.Float)
    hjp = db.Column(db.Float)
    effective_date = db.Column(db.Date)
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship("Product", back_populates="prices")
