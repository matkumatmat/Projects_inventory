# tests/test_admin_routes.py
import pytest
from flask_jwt_extended import create_access_token
from app.models import ProductBatch, StockLocation

def get_auth_headers(role='admin', identity='1'):
    """Helper untuk membuat header otentikasi."""
    token = create_access_token(identity=identity, additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}'}

def test_admin_inbound_success(client, db_session):
    """Tes sukses endpoint inbound oleh admin."""
    headers = get_auth_headers(role='admin')
    inbound_data = {
        "product_erp_id": "ADM-001",
        "product_name": "Produk Admin",
        "product_nie": "NIE-ADM",
        "batch_number": "BATCH-ADM-001",
        "receipt_qty": 100,
        "receipt_pic": "Admin User"
    }
    response = client.post('/api/admin/inbound/receive', json=inbound_data, headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['message'] == "Batch received successfully"

def test_admin_inbound_by_guest_fail(client, db_session):
    """Tes gagal endpoint inbound oleh guest."""
    headers = get_auth_headers(role='guest') # Role tidak diizinkan
    inbound_data = {"product_erp_id": "FAIL-001"}
    response = client.post('/api/admin/inbound/receive', json=inbound_data, headers=headers)
    assert response.status_code == 403 # Forbidden

def test_admin_inbound_no_jwt_fail(client, db_session):
    """Tes gagal endpoint inbound tanpa JWT."""
    inbound_data = {"product_erp_id": "FAIL-002"}
    response = client.post('/api/admin/inbound/receive', json=inbound_data)
    assert response.status_code == 401 # Unauthorized

# Anda bisa menambahkan lebih banyak tes untuk rute admin lainnya di sini
# Contoh:
# def test_admin_create_product_success(client, db_session):
#     ...
