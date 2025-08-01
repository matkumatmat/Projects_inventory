# app/models/tender_item.py
from app.utils.extensions import db

class TenderItem(db.Model):
    """
    Tabel pivot untuk mencatat distribusi item dari sebuah Tender.
    """
    __tablename__ = 'tender_items'
    id = db.Column(db.Integer, primary_key=True)

    # Foreign Key ke Tender utama
    tender_id = db.Column(db.Integer, db.ForeignKey('tenders.id'), nullable=False)

    quantity = db.Column(db.Integer, nullable=False)
    destination = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='DITITIP', nullable=False, comment="DITITIP, DIKIRIM")

    # Kolom untuk mencatat dari rak mana saja barang diambil. Disimpan sebagai JSON.
    # Contoh: '[{"rack_id": 1, "rack_code": "A-01-01", "quantity": 50}, ...]'
    racks_source = db.Column(db.JSON, nullable=True)

    # Relationship
    tender = db.relationship("Tender", back_populates="tender_items")
