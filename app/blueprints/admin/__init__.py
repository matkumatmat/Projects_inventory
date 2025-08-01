# app/blueprints/admin/__init__.py
from flask import Blueprint
from flask_jwt_extended import jwt_required
from functools import wraps
from flask import jsonify

from app.utils.auth_utils import roles_required # Asumsi ada helper untuk cek role

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Decorator untuk seluruh blueprint admin
@admin_bp.before_request
@jwt_required()
@roles_required('admin', 'superadmin')
def before_request():
    """Proteksi semua rute di blueprint admin."""
    pass

# Impor semua rute admin di sini
from .routes import product, inbound, warehouse, tender, consignment, shipment
