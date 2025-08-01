# app/blueprints/admin/routes/inbound.py
from flask import request, jsonify
from marshmallow import ValidationError

from .. import admin_bp
from ..schemas.inbound_schema import InboundSchema
from ..services.inbound_service import InboundService

@admin_bp.route('/inbound/receive', methods=['POST'])
def receive_batch():
    """
    Endpoint untuk menerima batch produk baru.
    Otentikasi dan otorisasi sudah ditangani oleh decorator di __init__.py blueprint.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    schema = InboundSchema()
    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    batch, error = InboundService.receive_new_batch(data)

    if error:
        return jsonify({"error": f"Failed to receive batch: {error}"}), 500

    return jsonify({
        "message": "Batch received successfully",
        "batch_id": batch.id,
        "initial_stock_location_id": batch.stock_locations[0].id
    }), 201
