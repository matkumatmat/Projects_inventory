# app/schemas/warehouse_schemas.py

from app.utils.extensions import ma
from app.models import *
from app.blueprints.products.schemas import ProductClassSchema # Impor dari file skema produk

class WarehouseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Warehouse
        load_instance = True
        include_fk = False

    racks = ma.Nested("RackSchema", many=True, exclude=("warehouse",))
    allowed_product_classes = ma.Nested(ProductClassSchema, many=True)

class RackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rack
        load_instance = True
        include_fk = True

    warehouse = ma.Nested(WarehouseSchema, exclude=("racks", "allowed_product_classes"))
