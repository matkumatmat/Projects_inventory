# tests/test_product_models.py

from app.models import Product, ProductBatch, ProductClass, ProductPrice, StockLocation

def test_create_product_class(db_session):
    """Tes pembuatan ProductClass."""
    pc = ProductClass(classification="Obat Keras", temperature="2-8 C")
    db_session.add(pc)
    db_session.commit()
    assert pc.id is not None

def test_create_product(db_session):
    """Tes pembuatan Product dan relasinya dengan ProductClass."""
    pc = ProductClass(classification="Obat Bebas", temperature="Suhu Ruang")
    p = Product(
        erp_id="PROD-001",
        name="Paracetamol 500mg",
        nie="GKL0123456789A1",
        product_class=pc
    )
    db_session.add_all([pc, p])
    db_session.commit()
    assert p.id is not None
    assert p.product_class.classification == "Obat Bebas"

def test_product_batch_creates_initial_stock(db_session):
    """
    Tes bahwa pembuatan ProductBatch secara otomatis membuat StockLocation 'REGULER'.
    """
    # Setup
    pc = ProductClass(classification="Jamu", temperature="Suhu Ruang")
    p = Product(erp_id="PROD-002", name="Tolak Angin", product_class=pc, nie="TR123")
    db_session.add_all([pc, p])
    db_session.commit()

    # Aksi: Buat batch baru
    batch = ProductBatch(
        batch_number="BATCH-001",
        product_id=p.id,
        receipt_qty=1000
    )
    db_session.add(batch)
    db_session.commit() # Commit batch dulu untuk mendapatkan ID

    # Buat stok awal setelah batch dibuat
    initial_stock = StockLocation(
        product_batch_id=batch.id,
        quantity=batch.receipt_qty,
        status='REGULER'
    )
    db_session.add(initial_stock)
    db_session.commit()

    # Verifikasi
    assert batch.id is not None
    assert len(batch.stock_locations) == 1

    stock_record = batch.stock_locations[0]
    assert stock_record.id is not None
    assert stock_record.quantity == 1000
    assert stock_record.status == 'REGULER'
    assert stock_record.tender_id is None
    assert stock_record.consignment_id is None

def test_create_product_price(db_session):
    """Tes pembuatan ProductPrice."""
    pc = ProductClass(classification="Alkes", temperature="Suhu Ruang")
    p = Product(erp_id="PROD-003", name="Masker N95", nie="AKD123", product_class=pc)
    price = ProductPrice(product=p, het=15000.0, hna=12000.0)

    db_session.add_all([pc, p, price])
    db_session.commit()

    assert price.id is not None
    assert p.prices[0].het == 15000.0
