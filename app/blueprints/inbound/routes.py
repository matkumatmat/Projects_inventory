# app/blueprints/inbound/routes.py
from flask import request, jsonify
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required

from . import inbound_bp
from .schemas import InboundSchema
from .services import InboundService

@inbound_bp.route('/receive', methods=['POST'])
@jwt_required()
def receive_batch():
    """
    Endpoint untuk menerima batch produk baru.
    Memerlukan otentikasi JWT.
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
        "product_id": batch.product_id,
        "initial_stock_location_id": batch.stock_locations[0].id
    }), 201
