# app/blueprints/inbound/schemas.py
from marshmallow import Schema, fields, validate

class InboundSchema(Schema):
    """Schema untuk validasi data penerimaan barang baru."""
    product_erp_id = fields.String(required=True)
    product_name = fields.String(required=True) # Diperlukan jika produk baru
    product_nie = fields.String(required=True)

    batch_number = fields.String(required=True)
    expiry_date = fields.Date(required=False, allow_none=True)
    receipt_qty = fields.Integer(required=True, validate=validate.Range(min=1))
    receipt_pic = fields.String(required=True)

    # Opsional, jika produk benar-benar baru
    product_class_name = fields.String(required=False)
    product_manufacturer = fields.String(required=False)
