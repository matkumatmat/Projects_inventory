# app/blueprints/inbound/__init__.py
from flask import Blueprint

inbound_bp = Blueprint('inbound', __name__, url_prefix='/api/inbound')

from . import routes
