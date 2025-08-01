# tests/test_superadmin_routes.py
import pytest
from flask_jwt_extended import create_access_token
from app.models import User

def get_auth_headers(role='superadmin', identity='1'):
    """Helper untuk membuat header otentikasi."""
    token = create_access_token(identity=identity, additional_claims={'role': role})
    return {'Authorization': f'Bearer {token}'}

def test_sa_create_user_success(client, db_session):
    """Tes sukses SuperAdmin membuat user baru."""
    headers = get_auth_headers(role='superadmin')
    user_data = {
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "supersecretpassword",
        "role": "admin"
    }
    response = client.post('/api/superadmin/users', json=user_data, headers=headers)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['username'] == 'newadmin'
    assert json_data['role'] == 'admin'

    # Verifikasi user ada di DB
    user = User.query.filter_by(username='newadmin').first()
    assert user is not None

def test_sa_create_user_by_admin_fail(client, db_session):
    """Tes gagal jika admin mencoba mengakses endpoint SuperAdmin."""
    headers = get_auth_headers(role='admin') # Role tidak diizinkan
    user_data = {"username": "failuser"}
    response = client.post('/api/superadmin/users', json=user_data, headers=headers)
    assert response.status_code == 403 # Forbidden

def test_sa_create_user_conflict(client, db_session):
    """Tes gagal jika user sudah ada."""
    # Buat user awal
    headers = get_auth_headers(role='superadmin')
    user_data = {
        "username": "existinguser",
        "email": "existing@example.com",
        "password": "password123"
    }
    client.post('/api/superadmin/users', json=user_data, headers=headers)

    # Coba buat lagi dengan username yang sama
    response = client.post('/api/superadmin/users', json=user_data, headers=headers)
    assert response.status_code == 409 # Conflict
    assert "Username already exists" in response.get_json()['error']
