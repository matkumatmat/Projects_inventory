# tests/test_outbound_models.py

from app.models import (
    ShipmentOrder, PackingSlip, PackedBox, PackedItem,
    StockLocation, Product, ProductBatch, ProductClass,
    Tender, TenderItem, Warehouse, Rack
)
import datetime

def setup_stock_location(db_session, unique_id=""):
    """Helper untuk membuat data lengkap hingga ke stock location."""
    wh = Warehouse(erp_id=f"WH-TEST-{unique_id}", building_name="Gudang Uji Coba")
    rack = Rack(rack_code=f"T-{unique_id}", column_no="01", row_no="01", rack_identifier=f"WH-TEST-{unique_id}-T-01-01", warehouse=wh)
    pc = ProductClass(classification=f"REGULER-{unique_id}", temperature="Suhu Ruang")
    p = Product(erp_id=f"PROD-TEST-{unique_id}", name="Produk Uji", product_class=pc, nie=f"GKLTEST{unique_id}")
    batch = ProductBatch(batch_number=f"BATCH-TEST-{unique_id}", product=p, receipt_qty=100)

    stock = StockLocation(
        product_batch=batch,
        rack=rack,
        quantity=100,
        status='REGULER'
    )
    db_session.add_all([wh, rack, pc, p, batch, stock])
    db_session.commit()
    return stock

def test_create_shipment_order(db_session):
    """Tes pembuatan ShipmentOrder untuk penjualan reguler."""
    so = ShipmentOrder(customer_id="CUST-001", customer_name="Apotech Sehat")
    db_session.add(so)
    db_session.commit()
    assert so.id is not None
    assert so.status == "PENDING"

def test_full_packing_process(db_session):
    """Tes alur lengkap dari PackingSlip, PackedBox, hingga PackedItem."""
    stock_location = setup_stock_location(db_session, "pack")

    so = ShipmentOrder(customer_id="CUST-002", customer_name="Toko Obat Sentosa")
    ps = PackingSlip(reference_no="PACK-001", shipment_order=so)
    box = PackedBox(box_number=1, packing_slip=ps)
    item = PackedItem(
        quantity=10,
        packed_box=box,
        stock_location_id=stock_location.id
    )

    # Simulasikan pengurangan stok
    stock_location.quantity -= 10

    db_session.add_all([so, ps, box, item])
    db_session.commit()

    assert item.id is not None
    assert box.packed_items[0].quantity == 10
    assert ps.packed_boxes[0].box_number == 1
    assert so.packing_slip.reference_no == "PACK-001"
    assert stock_location.quantity == 90 # Pastikan stok berkurang

def test_tender_and_tender_item(db_session):
    """Tes pembuatan Tender dan item distribusinya."""
    batch = setup_stock_location(db_session, "tender").product_batch

    tender = Tender(
        contract_no="TENDER-RS-HARAPAN",
        customer_id="RS-HARAPAN",
        product_batch_id=batch.id,
        total_qty=80
    )
    db_session.add(tender)
    db_session.commit()

    # Buat item distribusi untuk tender
    tender_item = TenderItem(
        tender_id=tender.id,
        quantity=30,
        destination="Gudang Farmasi RS Harapan",
        racks_source='[{"rack_id": 1, "quantity": 30}]' # Contoh data JSON
    )
    db_session.add(tender_item)
    db_session.commit()

    assert tender.id is not None
    assert len(tender.tender_items) == 1
    assert tender.tender_items[0].destination == "Gudang Farmasi RS Harapan"
    assert tender_item.tender.contract_no == "TENDER-RS-HARAPAN"
