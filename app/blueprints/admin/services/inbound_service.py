# app/blueprints/admin/services/inbound_service.py
from app.models import Product, ProductBatch, ProductClass, StockLocation
from app.utils.extensions import db

class InboundService:
    @staticmethod
    def receive_new_batch(data):
        """
        Menerima batch produk baru, membuat record yang relevan,
        dan membuat stok awal sebagai 'REGULER'.
        """
        try:
            # 1. Cari atau buat Product
            product = Product.query.filter_by(erp_id=data['product_erp_id']).first()
            if not product:
                # Cari atau buat ProductClass jika produk baru
                product_class_name = data.get('product_class_name', 'Umum')
                product_class = ProductClass.query.filter_by(classification=product_class_name).first()
                if not product_class:
                    product_class = ProductClass(classification=product_class_name)
                    db.session.add(product_class)

                product = Product(
                    erp_id=data['product_erp_id'],
                    name=data['product_name'],
                    nie=data['product_nie'],
                    manufacturer=data.get('product_manufacturer'),
                    product_class=product_class
                )
                db.session.add(product)

            # 2. Buat ProductBatch
            new_batch = ProductBatch(
                product=product,
                batch_number=data['batch_number'],
                expiry_date=data.get('expiry_date'),
                receipt_qty=data['receipt_qty'],
                receipt_pic=data['receipt_pic']
            )
            db.session.add(new_batch)

            # Flush untuk mendapatkan ID batch sebelum membuat stock location
            db.session.flush()

            # 3. Buat StockLocation awal
            initial_stock = StockLocation(
                product_batch_id=new_batch.id,
                quantity=new_batch.receipt_qty,
                status='REGULER'
            )
            db.session.add(initial_stock)

            db.session.commit()
            return new_batch, None
        except Exception as e:
            db.session.rollback()
            return None, str(e)
