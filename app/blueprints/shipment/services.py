# app/services/shipment_services.py (Versi Upgrade)

from app.models.outbound import *
from app.models.warehouse import *
from app.models.product import *
from app.utils.extensions import db
from sqlalchemy import func

class ShipmentService:
    @staticmethod
    def create_draft_shipment_order(data):
        """
        Hanya membuat 'draf' surat jalan. Tidak ada pengurangan stok di sini.
        """
        new_order = ShipmentOrder(**data)
        db.session.add(new_order)
        db.session.commit()
        return new_order

    @staticmethod
    def find_available_stock_for_packing(allocation_code):
        """
        Mencari stok yang tersedia untuk sebuah alokasi/kontrak dan 
        MENGURUTKANNYA berdasarkan FEFO untuk direkomendasikan ke tim packing.
        """
        # --- PERBAIKAN SYNTAX DI SINI ---
        available_stock = (db.session.query(
            StockLocation,
            ProductBatch.expiry_date,
            Product.name,
            ProductBatch.batch_number
        )
        .join(AllocationDetail)
        .join(Allocation)
        .join(ProductBatch)
        .join(Product)
        .filter(
            Allocation.allocation_code == allocation_code,
            StockLocation.quantity > 0,
            AllocationDetail.status == 'DITITIP'
        )
        .order_by(ProductBatch.expiry_date.asc()) # <-- KUNCI FEFO
        .all())
        # --- AKHIR PERBAIKAN ---

        recommendations = []
        for stock_loc, expiry, prod_name, batch_no in available_stock:
            recommendations.append({
                "stock_location_id": stock_loc.id,
                "product_name": prod_name,
                "batch_number": batch_no,
                "rack_identifier": stock_loc.rack.rack_identifier if stock_loc.rack else "PALLETE",
                "available_quantity": stock_loc.quantity,
                "expiry_date": expiry.isoformat()
            })
        
        return recommendations

    @staticmethod
    def execute_shipment(shipment_order_id, actual_ship_date):
        """
        Finalisasi pengiriman. Mengubah status dan mencatat tanggal kirim aktual.
        """
        order = ShipmentOrder.query.get(shipment_order_id)
        if not order or order.status != 'READY_TO_SHIP':
            raise ValueError("Order tidak ditemukan atau belum siap dikirim.")
        
        order.status = 'SHIPPED'
        order.actual_ship_date = actual_ship_date

        # Kumpulkan semua ID AllocationDetail yang unik dari order ini
        # untuk diubah statusnya menjadi 'DIKIRIM'.
        unique_allocation_detail_ids = set()
        if order.packing_slip:
            for box in order.packing_slip.packed_boxes:
                for item in box.packed_items:
                    # Dari item yang dipak, kita bisa tau asal lokasinya
                    stock_loc = item.stock_location
                    if stock_loc:
                        # Dari lokasi, kita bisa tau detail alokasinya
                        unique_allocation_detail_ids.add(stock_loc.allocation_detail_id)

        # Update status untuk setiap AllocationDetail yang unik
        for detail_id in unique_allocation_detail_ids:
            detail = AllocationDetail.query.get(detail_id)
            if detail:
                # Asumsi: jika sudah masuk proses shipment,
                # maka seluruh kuantitas untuk tujuan ini dianggap terkirim.
                detail.status = 'DIKIRIM'

        db.session.commit()
        return order

    @staticmethod
    def add_final_document(shipment_order_id, document_url):
        """Mencatat URL dokumen final dari Admin Office."""
        order = ShipmentOrder.query.get(shipment_order_id)
        if not order:
            raise ValueError("Order tidak ditemukan.")
            
        order.merged_document_url = document_url
        order.status = 'DOCUMENTED'
        db.session.commit()
        return order
