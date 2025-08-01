# app/models/tender.py
from ..extensions import db

class Tender(db.Model):
    """Tabel 'Pivot' atau Ledger untuk setiap kontrak Tender."""
    __tablename__ = 'tenders'
    id = db.Column(db.Integer, primary_key=True)
    contract_no = db.Column(db.String(100), unique=True, nullable=False)
    customer_id = db.Column(db.String(100), nullable=False)
    product_batch_id = db.Column(db.Integer, db.ForeignKey('product_batches.id'), nullable=False)
    total_qty = db.Column(db.Integer, nullable=False)
    realized_qty = db.Column(db.Integer, default=0, nullable=False)
    remaining_qty = db.Column(db.Integer, nullable=False)
    
    # --- KUNCI LOKASI ---
    # Mencatat di rak mana saja stok untuk tender ini berada.
    # Disimpan sebagai JSON untuk fleksibilitas.
    rack_locations = db.Column(db.JSON, nullable=True)

    product_batch = db.relationship("ProductBatch")
