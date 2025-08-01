# app/blueprints/superadmin/__init__.py
from flask import Blueprint
from flask_jwt_extended import jwt_required

from app.utils.auth_utils import roles_required

superadmin_bp = Blueprint('superadmin', __name__, url_prefix='/api/superadmin')

# Decorator untuk seluruh blueprint superadmin
@superadmin_bp.before_request
@jwt_required()
@roles_required('superadmin')
def before_request():
    """Proteksi semua rute di blueprint superadmin."""
    pass

# Impor rute superadmin
from .routes import user_management
