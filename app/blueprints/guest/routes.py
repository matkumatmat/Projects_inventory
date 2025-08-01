# app/blueprints/guest/routes.py
from flask import request, jsonify
from . import guest_bp
from .services import GuestService

@guest_bp.route('/product-details', methods=['GET'])
def get_product_details():
    """
    Endpoint publik untuk melihat detail produk, batch, dan stok.
    Menerima parameter query: ?erp_id=...&batch_number=...
    """
    erp_id = request.args.get('erp_id')
    batch_number = request.args.get('batch_number')

    if not erp_id:
        return jsonify({"error": "Parameter 'erp_id' diperlukan"}), 400

    details, error = GuestService.get_comprehensive_product_details(erp_id, batch_number)

    if error:
        return jsonify({"error": error}), 404

    return jsonify(details), 200
