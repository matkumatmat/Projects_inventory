# app/blueprints/guest/__init__.py
from flask import Blueprint

guest_bp = Blueprint('guest', __name__, url_prefix='/api/guest')

from . import routes
