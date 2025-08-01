# tests/test_warehouse_models.py

from app.models import Warehouse, Rack, StockLocation, Product, ProductBatch, ProductClass, Tender

def setup_product_data(db_session, unique_id=""):
    """Helper untuk membuat produk dan batch."""
    pc = ProductClass(classification=f"Vaksin {unique_id}", temperature="2-8 C")
    p = Product(erp_id=f"VAC-001-{unique_id}", name="Vaksin Polio", product_class=pc, nie=f"BKL123{unique_id}")
    batch = ProductBatch(batch_number=f"VAC-BATCH-01-{unique_id}", product=p, receipt_qty=500)
    db_session.add_all([pc, p, batch])
    db_session.commit()
    return batch

def test_create_warehouse(db_session):
    """Tes pembuatan Warehouse."""
    wh = Warehouse(erp_id="WH-JKT-01", building_name="Gudang Pusat Jakarta")
    db_session.add(wh)
    db_session.commit()
    assert wh.id is not None

def test_create_rack(db_session):
    """Tes pembuatan Rack dan relasinya dengan Warehouse."""
    wh = Warehouse(erp_id="WH-BDG-01", building_name="Gudang Bandung")
    rack = Rack(rack_code="A", column_no="01", row_no="01-05", rack_identifier="WH-BDG-01-A-01-01-05", warehouse=wh)
    db_session.add(rack)
    db_session.commit()
    assert rack.id is not None
    assert rack.warehouse.building_name == "Gudang Bandung"

def test_create_stock_location_as_reguler(db_session):
    """Tes pembuatan StockLocation dengan status default REGULER."""
    batch = setup_product_data(db_session, "wh-reg")
    wh = Warehouse(erp_id="WH-SBY-01", building_name="Gudang Surabaya")
    rack = Rack(rack_code="B", column_no="02", row_no="03", rack_identifier="WH-SBY-01-B-02-03", warehouse=wh)

    stock = StockLocation(
        quantity=100,
        product_batch_id=batch.id,
        rack=rack,
        status='REGULER' # Eksplisit untuk kejelasan
    )
    db_session.add_all([wh, rack, stock])
    db_session.commit()

    assert stock.id is not None
    assert stock.status == 'REGULER'
    assert stock.rack.rack_code == "B"
    assert stock.tender_id is None

def test_create_stock_location_for_tender(db_session):
    """Tes pembuatan StockLocation yang dialokasikan untuk Tender."""
    batch = setup_product_data(db_session, "wh-ten")
    tender = Tender(contract_no="TENDER-001", customer_id="CUST-T1", product_batch_id=batch.id, total_qty=50)

    stock = StockLocation(
        quantity=50,
        product_batch_id=batch.id,
        status='ALLOCATED_TENDER',
        tender=tender
    )
    db_session.add_all([tender, stock])
    db_session.commit()

    assert stock.id is not None
    assert stock.status == 'ALLOCATED_TENDER'
    assert stock.tender.contract_no == "TENDER-001"
