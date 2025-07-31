# app/schemas/allocation_schemas.py

from app.utils.extensions import ma
from app.models import *
from app.blueprints.warehouse.schemas import RackSchema # Impor dari file skema gudang

class AllocationTypeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AllocationType
        load_instance = True

class StockLocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = StockLocation
        load_instance = True
        include_fk = True

    rack = ma.Nested(RackSchema, only=("id", "rack_identifier"))

class AllocationDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = AllocationDetail
        load_instance = True
        include_fk = True

    locations = ma.Nested(StockLocationSchema, many=True, exclude=("allocation_detail",))

class AllocationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Allocation
        load_instance = True
        include_fk = True

    allocation_type = ma.Nested(AllocationTypeSchema)
    details = ma.Nested(AllocationDetailSchema, many=True, exclude=("allocation",))
    
    # Nested pake string biar gak circular import
    product_batch = ma.Nested("ProductBatchSchema", only=("id", "batch_number"))
