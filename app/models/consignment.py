# app/models/consignment.py
from app.utils.extensions import db

class Consignment(db.Model):
    """Mencatat setiap item yang dikirim secara konsinyasi."""
    __tablename__ = 'consignments'
    id = db.Column(db.Integer, primary_key=True)
    consignment_no = db.Column(db.String(100), unique=True, nullable=False)
    customer_id = db.Column(db.String(100), nullable=False)
    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Info Finansial
    total_value = db.Column(db.Float, nullable=False)
    paid_amount = db.Column(db.Float, default=0.0, nullable=False)
    remaining_value = db.Column(db.Float, nullable=False)
    
    status = db.Column(db.String(50), default='AT_CUSTOMER', nullable=False) # AT_CUSTOMER, SOLD, RETURNED

    product_batch = db.relationship("ProductBatch")
