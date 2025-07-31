# app/schemas/product_schemas.py

from app.utils.extensions import ma
from app.models import *

class ProductClassSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductClass
        load_instance = True

class ProductPriceSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductPrice
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product
        load_instance = True
        include_fk = True
    
    product_class = ma.Nested(ProductClassSchema, exclude=("products",))
    prices = ma.Nested(ProductPriceSchema, many=True, exclude=("product",))

class ProductDocSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductDoc
        load_instance = True

class ProductDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductDetail
        load_instance = True

class ProductBatchSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ProductBatch
        load_instance = True
        include_fk = True

    product = ma.Nested(ProductSchema, exclude=("batches",))
    details = ma.Nested(ProductDetailSchema, exclude=("batch",))
    docs = ma.Nested(ProductDocSchema, exclude=("batch",))
