# --- backend/app/blueprints/auth/routes.py ---
# Layer: API Endpoints
from marshmallow import ValidationError
from flask import Blueprint, request, jsonify
from app.utils.extensions import ma # Import Marshmallow instance
from .schemas import UserRegistrationSchema, UserLoginSchema, GoogleLoginSchema, UserSchema, UserEditSchema
from .services import register_user, authenticate_user, authenticate_with_google, get_user_by_id, update_user
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token # Import JWT decorators dan fungsi

# Inisialisasi Blueprint untuk modul otentikasi
auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1/auth')

# Inisialisasi schema untuk validasi dan serialisasi
registration_schema = UserRegistrationSchema()
login_schema = UserLoginSchema()
google_login_schema = GoogleLoginSchema() # Inisialisasi GoogleLoginSchema
user_schema = UserSchema()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Endpoint untuk registrasi pengguna baru.
    Menerima data JSON: username, email, password, (opsional: role, nik).
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(msg="No input data provided"), 400

    # Validasi input menggunakan schema
    try:
        data = registration_schema.load(json_data)
    except ma.ValidationError as err:
        raise err 

    # Panggil service untuk mendaftarkan pengguna
    user, error_message = register_user(data)

    if error_message:
        return jsonify(msg=error_message), 409 # Conflict jika username/email/NIK sudah ada

    # Serialisasi objek user yang baru dibuat untuk respons
    result = user_schema.dump(user)
    return jsonify(msg="User registered successfully", user=result), 201 # Created

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Endpoint untuk login pengguna.
    Menerima data JSON: username, password.
    Mengembalikan access_token dan refresh_token jika login berhasil.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(msg="No input data provided"), 400

    # Validasi input menggunakan schema
    try:
        data = login_schema.load(json_data)
    except ma.ValidationError as err:
        raise err

    # Panggil service untuk mengotentikasi pengguna
    access_token, refresh_token, user = authenticate_user(data['username'], data['password'])

    if not access_token:
        return jsonify(msg="Invalid credentials"), 401 # Unauthorized

    # Serialisasi objek user untuk respons
    result = user_schema.dump(user)
    return jsonify(
        msg="Logged in successfully",
        access_token=access_token,
        refresh_token=refresh_token,
        user=result
    ), 200

@auth_bp.route('/google-login', methods=['POST'])
def google_login():
    """
    Endpoint untuk login/registrasi pengguna via Google OAuth.
    Menerima Google ID Token dari frontend.
    """
    json_data = request.get_json()
    if not json_data:
        return jsonify(msg="No input data provided"), 400
    
    # Validasi input menggunakan schema
    try:
        data = google_login_schema.load(json_data)
    except ma.ValidationError as err:
        raise err

    id_token_str = data['id_token']
    
    # Panggil service untuk otentikasi/registrasi dengan Google
    access_token, refresh_token, user, error_message = authenticate_with_google(id_token_str)

    if error_message:
        return jsonify(msg=error_message), 401 # Unauthorized atau error verifikasi

    # Serialisasi objek user untuk respons
    result = user_schema.dump(user)
    return jsonify(
        msg="Logged in successfully via Google",
        access_token=access_token,
        refresh_token=refresh_token,
        user=result
    ), 200

@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True) # Membutuhkan refresh token
def refresh():
    """
    Endpoint untuk mendapatkan access token baru menggunakan refresh token.
    """
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify(access_token=new_access_token), 200

@auth_bp.route('/profile', methods=['GET'])
@jwt_required() # Membutuhkan access token
def get_current_user():
    """
    Endpoint untuk mendapatkan detail pengguna yang sedang login.
    Membutuhkan access token yang valid.
    """
    user_id = get_jwt_identity() # Mengambil ID pengguna dari token
    user = get_user_by_id(user_id)

    if not user:
        return jsonify(msg="User not found"), 404 # Seharusnya tidak terjadi jika token valid

    result = user_schema.dump(user)
    return jsonify(user=result), 200

@auth_bp.route('/profile/update', methods=['PUT'])
@jwt_required() # Membutuhkan access token
def update_current_user():
    """
    Endpoint untuk memperbarui data pengguna yang sedang login.
    Membutuhkan access token yang valid.
    """
    user_id = get_jwt_identity() # Mengambil ID pengguna dari token
    json_data = request.get_json()
    if not json_data:
        return jsonify(msg="No input data provided"), 400
    
    user_edit_schema = UserEditSchema() # Ini yang menginisialisasi

    # Validasi input menggunakan UserEditSchema
    # partial=True memungkinkan update sebagian field saja
    try:
        data = user_edit_schema.load(json_data, partial=True) 
    except ma.ValidationError as err:
        raise err

    # Panggil service untuk memperbarui pengguna
    updated_user, error_message = update_user(user_id, data)

    if error_message:
        return jsonify(msg=error_message), 409 # Conflict jika username/email/NIK sudah ada

    if not updated_user:
        return jsonify(msg="User not found"), 404 # Seharusnya tidak terjadi jika token valid

    result = user_schema.dump(updated_user)
    return jsonify(msg="User updated successfully", user=result), 200


