# tests/test_guest_routes.py
import pytest
from app.models import Product, ProductBatch, ProductClass, StockLocation, Rack, Warehouse

def setup_test_product(db_session):
    """Membuat data produk untuk di-query oleh guest."""
    pc = ProductClass(classification="Obat Generik")
    p = Product(erp_id="GUEST-PROD", name="Ambroxol", nie="GKL998877", product_class=pc)
    batch = ProductBatch(product=p, batch_number="GUEST-BATCH", receipt_qty=1000)
    wh = Warehouse(erp_id="WH-GUEST", building_name="Gudang Publik")
    rack = Rack(rack_code="G", column_no="1", row_no="1", rack_identifier="WH-GUEST-G-1-1", warehouse=wh)
    stock = StockLocation(product_batch=batch, rack=rack, quantity=500, status='REGULER')
    db_session.add_all([pc, p, batch, wh, rack, stock])
    db_session.commit()

def test_guest_get_product_details_success(client, db_session):
    """Tes sukses endpoint detail produk oleh guest."""
    setup_test_product(db_session)

    response = client.get('/api/guest/product-details?erp_id=GUEST-PROD&batch_number=GUEST-BATCH')

    assert response.status_code == 200
    data = response.get_json()

    assert data['product']['erp_id'] == 'GUEST-PROD'
    assert data['batch']['batch_number'] == 'GUEST-BATCH'
    assert data['stock_summary']['REGULER'] == 500
    assert len(data['locations']) == 1
    assert data['locations'][0]['rack'] == 'WH-GUEST-G-1-1'

def test_guest_get_product_not_found(client, db_session):
    """Tes kasus jika produk atau batch tidak ditemukan."""
    response = client.get('/api/guest/product-details?erp_id=NOT-FOUND')
    assert response.status_code == 404
    assert 'Batch produk tidak ditemukan' in response.get_json()['error']

def test_guest_get_product_missing_param(client, db_session):
    """Tes kasus jika parameter erp_id hilang."""
    response = client.get('/api/guest/product-details')
    assert response.status_code == 400
    assert "Parameter 'erp_id' diperlukan" in response.get_json()['error']
