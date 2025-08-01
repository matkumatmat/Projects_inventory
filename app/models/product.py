# app/models/product_models.py

from app.utils.extensions import db
import datetime

class ProductClass(db.Model):
    __tablename__ = 'product_classes'
    id = db.Column(db.Integer, primary_key=True)
    classification = db.Column(db.String(50), unique=True, nullable=False)
    temperature = db.Column(db.String(50), nullable=True)
    products = db.relationship("Product", back_populates="product_class")


class Product(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    erp_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    manufacturer = db.Column(db.String(255), nullable=True)
    nie = db.Column(db.String(100), nullable=False)
    product_class_id = db.Column(db.Integer, db.ForeignKey('product_classes.id'))
    product_class = db.relationship("ProductClass", back_populates="products")
    batches = db.relationship("ProductBatch", back_populates="product", cascade="all, delete-orphan")
    prices = db.relationship("ProductPrice", back_populates="product", cascade="all, delete-orphan")

class ProductBatch(db.Model):
    __tablename__ = 'product_batches'

    id = db.Column(db.Integer, primary_key=True)
    batch_number = db.Column(db.String(100), nullable=False, unique=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    expiry_date = db.Column(db.Date)
    manufacture_date = db.Column(db.Date)
    receipt_date = db.Column(db.Date, default=datetime.date.today)
    receipt_qty = db.Column(db.Integer, nullable=False)
    receipt_pic = db.Column(db.String(100), nullable=True)
    receipt_doc_url = db.Column(db.String(512), nullable=True)
    length = db.Column(db.Float, nullable=True)
    width = db.Column(db.Float, nullable=True)
    height = db.Column(db.Float, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    front_url = db.Column(db.String(255), nullable=True)
    right_url = db.Column(db.String(255), nullable=True)
    left_url = db.Column(db.String(255), nullable=True)
    back_url = db.Column(db.String(255), nullable=True)
    group_url = db.Column(db.String(255), nullable=True)
    leaflet_url = db.Column(db.String(255), nullable=True)        
    product = db.relationship("Product", back_populates="batches")


class ProductPrice(db.Model):
    __tablename__ = 'product_prices'

    id = db.Column(db.Integer, primary_key=True)
    het = db.Column(db.Float)
    hna = db.Column(db.Float)
    hjp = db.Column(db.Float)
    effective_date = db.Column(db.Date)
    
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
    product = db.relationship("Product", back_populates="prices")
