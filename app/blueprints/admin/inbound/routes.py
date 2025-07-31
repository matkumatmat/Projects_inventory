# app/blueprints/admin/inbound/inbound_routes.py
# Fokus: Hanya untuk proses penerimaan barang.

from flask import Blueprint, request, jsonify
from ...products.services import ProductService
from ...products.schemas import ProductBatchSchema

# Inisialisasi Blueprint baru khusus untuk inbound
inbound_bp = Blueprint('inbound_bp', __name__, url_prefix='/api/admin/inbound')

@inbound_bp.route('/', methods=['POST'])
# @admin_required
def process_inbound_route():
    """
    Endpoint untuk memproses penerimaan barang baru (inbound).
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body tidak boleh kosong"}), 400
    
    try:
        new_batch = ProductService.process_inbound_batch(data)
        schema = ProductBatchSchema()
        return jsonify(schema.dump(new_batch)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({"error": "Terjadi kesalahan internal saat memproses inbound"}), 500

