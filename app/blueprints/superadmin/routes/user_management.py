# app/blueprints/superadmin/routes/user_management.py
from flask import request, jsonify
from marshmallow import ValidationError

from .. import superadmin_bp
from ...auth.services import register_user
from ...auth.schemas import UserRegistrationSchema

@superadmin_bp.route('/users', methods=['POST'])
def create_user():
    """
    Endpoint khusus SuperAdmin untuk membuat pengguna baru (misal, admin).
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify({"error": "No input data provided"}), 400

    try:
        # Gunakan skema registrasi yang sudah ada
        data = UserRegistrationSchema().load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # Panggil service registrasi
    new_user, error = register_user(data)

    if error:
        return jsonify({"error": error}), 409 # 409 Conflict (e.g., username/email exists)

    return jsonify({
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username,
        "role": new_user.role
    }), 201
