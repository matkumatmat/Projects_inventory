# app/services/product_services.py
# Fokus: Definisi Produk, Batch, dan Laporan per Produk

from app.models.product import *
from app.models.warehouse import *
from app.utils.extensions import db
from sqlalchemy import func
import datetime


class ProductService:
    @staticmethod
    def process_inbound_batch(data):
        """
        Logika 'Pintar' untuk penerimaan barang.
        Mengecek produk, membuat batch, dan alokasi reguler awal.
        """
        # ... (kode sama seperti sebelumnya) ...
        product = Product.query.filter_by(erp_id=data['erp_id']).first()
        if not product:
            product_data = {
                'erp_id': data['erp_id'],
                'name': data['product_name'],
                'manufacturer': data.get('manufacturer'),
                'product_class_id': data.get('product_class_id')
            }
            product = Product(**product_data)
            db.session.add(product)
        new_batch = ProductBatch(
            product=product,
            batch_number=data['batch_number'],
            expiry_date=data.get('expiry_date')
        )
        db.session.add(new_batch)
        if data.get('details'):
            db.session.add(ProductDetail(batch=new_batch, **data['details']))
        if data.get('docs'):
            db.session.add(ProductDoc(batch=new_batch, **data['docs']))
        reguler_type = AllocationType.query.filter_by(name='reguler').first()
        if not reguler_type:
            db.session.rollback()
            raise ValueError("Tipe alokasi 'reguler' tidak ditemukan.")
        initial_allocation = Allocation(
            product_batch=new_batch,
            allocation_type=reguler_type,
            allocation_code=f"REG-{new_batch.batch_number}-{int(datetime.datetime.utcnow().timestamp())}",
            total_quantity=data['quantity']
        )
        db.session.add(initial_allocation)
        initial_detail = AllocationDetail(
            allocation=initial_allocation,
            quantity=data['quantity'],
            status='DITITIP'
        )
        db.session.add(initial_detail)
        initial_location = StockLocation(
            allocation_detail=initial_detail,
            quantity=data['quantity'],
            rack_id=None
        )
        db.session.add(initial_location)
        db.session.commit()
        return new_batch

    @staticmethod
    def get_stock_by_product(erp_id):
        """Laporan Sudut Pandang Produk (Total Stok) untuk Frontend."""
        # ... (kode sama seperti sebelumnya) ...
        total_stock = db.session.query(
            func.sum(StockLocation.quantity)
        ).join(AllocationDetail).join(Allocation).join(ProductBatch).join(Product)\
         .filter(Product.erp_id == erp_id)\
         .scalar()
        product = Product.query.filter_by(erp_id=erp_id).first()
        return {
            "erp_id": erp_id,
            "product_name": product.name if product else "N/A",
            "total_stock_across_all_locations": total_stock or 0
        }

    # --- FUNGSI BARU YANG DITAMBAHKAN ---
    @staticmethod
    def get_batch_stock_summary(batch_id):
        """
        Memberikan ringkasan stok lengkap untuk satu batch.
        Ini adalah fungsi "report" yang sangat penting.
        """
        results = db.session.query(
            AllocationType.name,
            AllocationDetail.destination,
            AllocationDetail.status,
            func.sum(StockLocation.quantity).label('total_quantity'),
            Rack.rack_identifier
        ).select_from(ProductBatch)\
         .join(Allocation, ProductBatch.id == Allocation.product_batch_id)\
         .join(AllocationType, Allocation.allocation_type_id == AllocationType.id)\
         .join(AllocationDetail, Allocation.id == AllocationDetail.allocation_id)\
         .join(StockLocation, AllocationDetail.id == StockLocation.allocation_detail_id)\
         .outerjoin(Rack, StockLocation.rack_id == Rack.id)\
         .filter(ProductBatch.id == batch_id)\
         .group_by(
            AllocationType.name, 
            AllocationDetail.destination, 
            AllocationDetail.status, 
            Rack.rack_identifier
         ).all()

        if not results:
            return {"batch_id": batch_id, "summary": "Stok tidak ditemukan atau masih kosong."}

        summary = {}
        total_stock = 0
        for name, dest, status, qty, rack in results:
            total_stock += qty
            if name not in summary:
                summary[name] = []
            
            location = rack if rack else "PALLETE"
            summary[name].append({
                "destination": dest,
                "status": status,
                "quantity": qty,
                "location": location
            })
        
        return {
            "batch_id": batch_id,
            "calculated_actual_stock": total_stock,
            "summary_by_allocation": summary
        }
