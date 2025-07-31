# app/services/packing_services.py

from app.models.outbound import *
from app.models.warehouse import *
from app.utils.extensions import db

class PackingService:
    @staticmethod
    def start_packing_process(shipment_order_id):
        """
        Memulai proses packing dengan membuat PackingSlip untuk sebuah ShipmentOrder.
        """
        order = ShipmentOrder.query.get(shipment_order_id)
        if not order or order.packing_slip:
            raise ValueError("Order tidak ditemukan atau sudah memiliki packing slip.")

        # Buat nomor referensi unik
        ref_no = f"PACK-{order.id}-{int(datetime.datetime.utcnow().timestamp())}"
        
        new_slip = PackingSlip(
            shipment_order=order,
            reference_no=ref_no
        )
        
        # Update status order
        order.status = 'PACKING'
        
        db.session.add(new_slip)
        db.session.commit()
        return new_slip

    @staticmethod
    def pack_items_into_box(packing_slip_id, box_number, items_to_pack):
        """
        Mencatat item ke dalam box dan LANGSUNG MENGURANGI STOK.
        'items_to_pack' adalah list of dict: 
        [{"stock_location_id": 1, "quantity": 10}, {"stock_location_id": 5, "quantity": 2}]
        """
        try:
            # 1. Buat record PackedBox
            new_box = PackedBox(
                packing_slip_id=packing_slip_id,
                box_number=box_number
            )
            db.session.add(new_box)

            # 2. Proses setiap item yang dimasukkan ke box
            for item_data in items_to_pack:
                stock_loc = StockLocation.query.get(item_data['stock_location_id'])
                
                # Validasi: Pastikan stok cukup
                if not stock_loc or stock_loc.quantity < item_data['quantity']:
                    raise ValueError(f"Stok di lokasi {stock_loc.id} tidak cukup.")
                
                # --- INI KUNCINYA: STOK LANGSUNG DIKURANGI DI SINI ---
                stock_loc.quantity -= item_data['quantity']
                
                # Buat record 'bukti pengambilan' (PackedItem)
                new_packed_item = PackedItem(
                    packed_box=new_box,
                    stock_location=stock_loc,
                    quantity=item_data['quantity']
                )
                db.session.add(new_packed_item)
            
            db.session.commit()
            return new_box
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def finalize_packing(packing_slip_id, data):
        """
        Mengupdate data final di PackingSlip dan mengubah status order.
        'data' berisi: packer_code, checker_staff, dll.
        """
        slip = PackingSlip.query.get(packing_slip_id)
        if not slip:
            raise ValueError("Packing slip tidak ditemukan.")
            
        slip.packer_code = data.get('packer_code')
        slip.checker_staff = data.get('checker_staff')
        
        # Update status order menjadi siap kirim
        slip.shipment_order.status = 'READY_TO_SHIP'
        
        db.session.commit()
        return slip
