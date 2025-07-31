# app/services/warehouse_services.py
# Fokus: Manajemen Fisik Gudang, Rak, dan Laporan per Gudang

from app.models.warehouse import *
from app.models.product import *
from app.utils.extensions import db
from sqlalchemy import func

class WarehouseService:
    @staticmethod
    def create_rack(data):
        """Membuat rak baru dan men-generate ID uniknya."""
        # ... (kode sama seperti sebelumnya) ...
        warehouse = Warehouse.query.get(data['warehouse_id'])
        if not warehouse:
            raise ValueError("Warehouse tidak ditemukan")
        identifier = f"{warehouse.erp_id}-{data.get('kolom', 'N/A')}-{data.get('baris', 'N/A')}"
        new_rack = Rack(
            rack_identifier=identifier,
            warehouse_id=data['warehouse_id'],
            kolom=data.get('kolom'),
            baris=data.get('baris'),
            properties=data.get('properties', {})
        )
        db.session.add(new_rack)
        db.session.commit()
        return new_rack

    @staticmethod
    def check_rack_availability(rack_id, allocation_detail_id_to_add):
        """Mengecek apakah sebuah rak bisa diisi berdasarkan aturan ketat."""
        # ... (kode sama seperti sebelumnya) ...
        existing_stock = StockLocation.query.filter_by(rack_id=rack_id).first()
        if not existing_stock:
            return {"available": True, "reason": "Rak kosong"}
        existing_alloc_detail = existing_stock.allocation_detail
        new_alloc_detail = AllocationDetail.query.get(allocation_detail_id_to_add)
        if existing_alloc_detail.allocation.product_batch_id != new_alloc_detail.allocation.product_batch_id:
            return {"available": False, "reason": "Beda batch"}
        if existing_alloc_detail.allocation_id != new_alloc_detail.allocation_id:
            return {"available": False, "reason": "Beda alokasi (kontrak)"}
        return {"available": True, "reason": "Batch dan alokasi sama"}

    @staticmethod
    def get_stock_by_warehouse(warehouse_id):
        """Laporan Sudut Pandang Gudang untuk Frontend."""
        results = db.session.query(
            Product.name,
            ProductBatch.batch_number,
            Allocation.allocation_code,
            AllocationType.name.label('allocation_type'),
            func.sum(StockLocation.quantity).label('quantity'),
            Rack.rack_identifier
        ).select_from(Warehouse)\
         .join(Rack).join(StockLocation).join(AllocationDetail).join(Allocation)\
         .join(ProductBatch).join(Product)\
         .filter(Warehouse.id == warehouse_id)\
         .group_by(Product.name, ProductBatch.batch_number, Allocation.allocation_code, AllocationType.name, Rack.rack_identifier)\
         .all()
        
        return [row._asdict() for row in results]
