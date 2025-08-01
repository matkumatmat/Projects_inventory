# app/blueprints/allocations/services.py
from app.models import StockLocation, Tender
from app.utils.extensions import db
from sqlalchemy.orm import joinedload

class AllocationService:
    @staticmethod
    def allocate_stock_to_tender(product_batch_id, tender_id, quantity_to_allocate):
        """
        Mengalokasikan stok dari 'REGULER' ke 'ALLOCATED_TENDER'.
        Ini adalah implementasi dari proses "pengeluaran" dari stok bebas ke tender.
        """
        try:
            # 1. Cari stok reguler yang tersedia untuk batch ini
            source_stock = StockLocation.query.filter_by(
                product_batch_id=product_batch_id,
                status='REGULER'
            ).first()

            if not source_stock or source_stock.quantity < quantity_to_allocate:
                raise ValueError("Stok reguler tidak mencukupi untuk dialokasikan.")

            # 2. Kurangi kuantitas dari stok reguler
            source_stock.quantity -= quantity_to_allocate

            # 3. Buat record stok baru yang dialokasikan untuk tender
            # Cek dulu apakah sudah ada stok untuk tender ini di lokasi yang sama (misal, palet)
            existing_tender_stock = StockLocation.query.filter_by(
                product_batch_id=product_batch_id,
                tender_id=tender_id,
                rack_id=source_stock.rack_id # Asumsi dipindah di lokasi yg sama dulu
            ).first()

            if existing_tender_stock:
                existing_tender_stock.quantity += quantity_to_allocate
            else:
                new_tender_stock = StockLocation(
                    product_batch_id=product_batch_id,
                    quantity=quantity_to_allocate,
                    status='ALLOCATED_TENDER',
                    tender_id=tender_id,
                    rack_id=source_stock.rack_id # Awalnya di lokasi yang sama
                )
                db.session.add(new_tender_stock)

            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def get_stock_by_tender(contract_no):
        """
        Menampilkan rincian stok yang dialokasikan untuk sebuah kontrak tender.
        """
        tender = Tender.query.filter_by(contract_no=contract_no).options(
            joinedload(Tender.stock_locations).joinedload(StockLocation.rack)
        ).first()

        if not tender:
            return None

        stock_details = []
        for stock in tender.stock_locations:
            stock_details.append({
                "quantity": stock.quantity,
                "status": stock.status,
                "rack": stock.rack.rack_identifier if stock.rack else "PALLETE"
            })

        return {
            "contract_no": tender.contract_no,
            "total_allocated": sum(s['quantity'] for s in stock_details),
            "details": stock_details
        }
