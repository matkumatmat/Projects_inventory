# tests/test_inbound_routes.py

import pytest
from flask_jwt_extended import create_access_token
from app.models import Product, ProductBatch, StockLocation

def test_receive_batch_success(client, db_session):
    """
    Tes kasus sukses untuk endpoint POST /api/inbound/receive.
    """
    # Buat token akses dengan identity sebagai string
    access_token = create_access_token(identity="1", additional_claims={'role': 'admin'})
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Data inbound yang valid
    inbound_data = {
        "product_erp_id": "ERP-001",
        "product_name": "Vitamin C 500mg",
        "product_nie": "POM-12345",
        "batch_number": "VC-BATCH-001",
        "receipt_qty": 500,
        "receipt_pic": "John Doe",
        "product_class_name": "Suplemen"
    }

    response = client.post('/api/inbound/receive', json=inbound_data, headers=headers)

    # Verifikasi respons
    assert response.status_code == 201, f"Expected 201, got {response.status_code}. Response: {response.get_data(as_text=True)}"
    json_response = response.get_json()
    assert json_response['message'] == "Batch received successfully"

    # Verifikasi data di database
    batch = db_session.get(ProductBatch, json_response['batch_id'])
    assert batch is not None
    assert batch.batch_number == "VC-BATCH-001"

    stock = db_session.get(StockLocation, json_response['initial_stock_location_id'])
    assert stock is not None
    assert stock.quantity == 500
    assert stock.status == 'REGULER'

def test_receive_batch_no_auth(client):
    """
    Tes kasus gagal karena tidak ada token otentikasi.
    """
    inbound_data = {"product_erp_id": "ERP-001"}
    response = client.post('/api/inbound/receive', json=inbound_data)
    assert response.status_code == 401

def test_receive_batch_invalid_data(client, db_session):
    """
    Tes kasus gagal karena data tidak valid (missing required field).
    """
    # Buat token akses dengan identity sebagai string
    access_token = create_access_token(identity="1", additional_claims={'role': 'admin'})
    headers = {'Authorization': f'Bearer {access_token}'}

    # Data tidak valid (receipt_qty hilang)
    inbound_data = {
        "product_erp_id": "ERP-002",
        "product_name": "Obat Batuk",
        "product_nie": "POM-67890",
        "batch_number": "OB-BATCH-002",
        "receipt_pic": "Jane Doe"
    }

    response = client.post('/api/inbound/receive', json=inbound_data, headers=headers)

    assert response.status_code == 422
    json_response = response.get_json()
    assert 'receipt_qty' in json_response
    assert json_response['receipt_qty'][0] == "Missing data for required field."
