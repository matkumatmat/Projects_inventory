# app/blueprints/guest/services.py
from app.models import Product, ProductBatch, StockLocation
from sqlalchemy.orm import joinedload

class GuestService:
    @staticmethod
    def get_comprehensive_product_details(erp_id, batch_number):
        """
        Mengambil detail produk yang komprehensif untuk ditampilkan ke guest.
        """
        query = ProductBatch.query.options(
            joinedload(ProductBatch.product).joinedload(Product.product_class),
            joinedload(ProductBatch.stock_locations).joinedload(StockLocation.rack)
        ).join(Product).filter(Product.erp_id == erp_id)

        if batch_number:
            query = query.filter(ProductBatch.batch_number == batch_number)

        batch = query.first()

        if not batch:
            return None, "Batch produk tidak ditemukan"

        # Olah data untuk respons
        product_info = {
            "name": batch.product.name,
            "erp_id": batch.product.erp_id,
            "nie": batch.product.nie,
            "manufacturer": batch.product.manufacturer,
            "product_class": batch.product.product_class.classification
        }

        batch_info = {
            "batch_number": batch.batch_number,
            "expiry_date": batch.expiry_date.isoformat() if batch.expiry_date else None,
            "receipt_qty": batch.receipt_qty
        }

        stock_summary = {
            "REGULER": 0,
            "ALLOCATED_TENDER": 0,
            "CONSIGNED": 0
        }

        locations = []
        for stock in batch.stock_locations:
            status = stock.status
            if status in stock_summary:
                stock_summary[status] += stock.quantity

            locations.append({
                "rack": stock.rack.rack_identifier if stock.rack else "PALLETE",
                "quantity": stock.quantity,
                "status": status
            })

        return {
            "product": product_info,
            "batch": batch_info,
            "stock_summary": stock_summary,
            "locations": locations
        }, None
