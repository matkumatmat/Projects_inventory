# app/services/allocation_services.py
# Layer: Logika Bisnis untuk Alokasi & Pergerakan Stok

from app.models.warehouse import *
from app.utils.extensions import db
from app.blueprints.warehouse.services import * # Panggil service lain
import datetime

# app/services/allocation_services.py
# Fokus: Alur Bisnis Alokasi, Re-alokasi, dan Pergerakan Stok
from app.blueprints.warehouse.services import * # Panggil service lain

class AllocationService:
    @staticmethod
    def reallocate_stock(data):
        """
        Logika untuk me-realokasi stok dari satu alokasi ke alokasi baru.
        Contoh: dari 'reguler' ke 'tender'.
        'data' harus berisi: source_batch_id, quantity_to_move, 
                             new_allocation_code, new_allocation_type_id, new_destination
        """
        try:
            # 1. Cari alokasi sumber (misal: reguler)
            source_allocation_detail = AllocationDetail.query.join(Allocation).filter(
                Allocation.product_batch_id == data['source_batch_id'],
                Allocation.allocation_type.has(name='reguler') # Asumsi sumbernya reguler
            ).first()

            if not source_allocation_detail or source_allocation_detail.quantity < data['quantity_to_move']:
                raise ValueError("Stok reguler tidak cukup atau tidak ditemukan.")

            # 2. Kurangi kuantitas di alokasi sumber
            source_allocation_detail.quantity -= data['quantity_to_move']
            source_allocation_detail.allocation.total_quantity -= data['quantity_to_move']

            # 3. Buat alokasi baru (misal: tender)
            new_allocation = Allocation(
                product_batch_id=data['source_batch_id'],
                allocation_type_id=data['new_allocation_type_id'],
                allocation_code=data['new_allocation_code'],
                total_quantity=data['quantity_to_move']
            )
            db.session.add(new_allocation)

            # 4. Buat detail tujuan untuk alokasi baru ini
            new_detail = AllocationDetail(
                allocation=new_allocation,
                quantity=data['quantity_to_move'],
                destination=data.get('new_destination'),
                status='DITITIP'
            )
            db.session.add(new_detail)

            # 5. Pindahkan stok fisiknya (secara virtual)
            # Kurangi stok di palet dari alokasi sumber
            source_location = StockLocation.query.filter_by(
                allocation_detail_id=source_allocation_detail.id,
                rack_id=None
            ).first()
            if not source_location or source_location.quantity < data['quantity_to_move']:
                raise ValueError("Stok fisik di palet tidak cukup untuk dipindahkan.")
            source_location.quantity -= data['quantity_to_move']
            
            # Buat catatan lokasi baru untuk alokasi baru, juga di palet
            new_location = StockLocation(
                allocation_detail=new_detail,
                quantity=data['quantity_to_move'],
                rack_id=None
            )
            db.session.add(new_location)

            db.session.commit()
            return new_allocation
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def assign_stock_to_rack(allocation_detail_id, rack_id, quantity):
        """Memindahkan stok dari palet ke rak spesifik."""
        # ... (kode sama seperti sebelumnya) ...
        check = WarehouseService.check_rack_availability(rack_id, allocation_detail_id)
        if not check['available']:
            raise ValueError(f"Tidak bisa menempatkan di rak: {check['reason']}")
        stock_on_palette = StockLocation.query.filter_by(allocation_detail_id=allocation_detail_id, rack_id=None).first()
        if not stock_on_palette or stock_on_palette.quantity < quantity:
            raise ValueError("Kuantitas di palet tidak mencukupi.")
        stock_on_palette.quantity -= quantity
        new_rack_stock = StockLocation(
            quantity=quantity,
            allocation_detail_id=allocation_detail_id,
            rack_id=rack_id
        )
        db.session.add(new_rack_stock)
        db.session.commit()
        return new_rack_stock

    @staticmethod
    def get_stock_by_allocation(allocation_code):
        """Laporan Sudut Pandang Alokasi (Kontrak) untuk Frontend."""
        results = db.session.query(
            Product.name,
            ProductBatch.batch_number,
            AllocationDetail.destination,
            AllocationDetail.status,
            StockLocation.quantity,
            Warehouse.building_name,
            Rack.rack_identifier
        ).select_from(Allocation)\
         .join(AllocationDetail).join(StockLocation).outerjoin(Rack).outerjoin(Warehouse)\
         .join(ProductBatch).join(Product)\
         .filter(Allocation.allocation_code == allocation_code)\
         .all()
        return [row._asdict() for row in results]
