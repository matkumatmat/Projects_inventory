# --- backend/app/blueprints/auth/services.py ---
# Layer: Business Logic

from app.models.user import User
from app.utils.extensions import db # Import db dari ekstensi
from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from google.oauth2 import id_token # Import untuk verifikasi Google ID Token
from google.auth.transport import requests # Import untuk request ke Google API
from flask import current_app # Untuk mengakses app.config

def register_user(data):
    """
    Mendaftarkan pengguna baru ke database.
    Args:
        data (dict): Data pengguna dari request (username, email, password, role, nik).
    Returns:
        User: Objek User yang baru dibuat jika berhasil, None jika username/email/NIK sudah ada.
    """
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'guest') # Default role guest
    nik = data.get('nik')

    # Cek apakah username, email, atau NIK sudah ada
    if User.query.filter_by(username=username).first():
        return None, "Username already exists."
    if User.query.filter_by(email=email).first():
        return None, "Email already exists."
    if nik and User.query.filter_by(nik=nik).first(): # Cek NIK hanya jika diberikan
        return None, "NIK already exists."

    new_user = User(username=username, email=email, password=password, role=role, nik=nik)
    db.session.add(new_user)
    db.session.commit()
    return new_user, None

def authenticate_user(username, password):
    """
    Mengotentikasi pengguna dan membuat token JWT jika kredensial valid.
    Args:
        username (str): Username pengguna.
        password (str): Password pengguna.
    Returns:
        tuple: (access_token, refresh_token, user_object) jika berhasil,
               (None, None, None) jika kredensial tidak valid.
    """
    user = User.query.filter_by(username=username).first()

    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=str(user.id))
        
        return access_token, refresh_token, user
    return None, None, None

def authenticate_with_google(id_token_str):
    """
    Mengotentikasi atau mendaftarkan pengguna via Google ID Token.
    Args:
        id_token_str (str): Google ID Token string dari frontend.
    Returns:
        tuple: (access_token, refresh_token, user_object) jika berhasil,
               (None, None, None, error_message) jika gagal.
    """
    try:
        # Verifikasi Google ID Token
        # Pastikan GOOGLE_CLIENT_ID sudah diset di app.config
        google_client_id = current_app.config.get('GOOGLE_CLIENT_ID')
        if not google_client_id:
            current_app.logger.error("GOOGLE_CLIENT_ID not configured for Google OAuth.")
            return None, None, None, "Server configuration error."

        idinfo = id_token.verify_oauth2_token(id_token_str, requests.Request(), google_client_id)

        google_user_id = idinfo['sub'] # ID unik pengguna dari Google
        email = idinfo['email']
        username = idinfo.get('name', email.split('@')[0]) # Ambil nama atau bagian email sebelum '@'
        
        # 1. Cek apakah user sudah ada dengan google_id ini
        user = User.query.filter_by(google_id=google_user_id).first()

        if user:
            # User sudah ada, langsung login
            current_app.logger.info(f"User {user.username} logged in via Google.")
        else:
            # 2. Jika belum ada dengan google_id, cek apakah email sudah terdaftar
            user = User.query.filter_by(email=email).first()
            if user:
                # Email sudah terdaftar, link akun Google ke user yang sudah ada
                user.google_id = google_user_id
                db.session.commit()
                current_app.logger.info(f"Google ID linked to existing user {user.username}.")
            else:
                # 3. Jika belum ada sama sekali, buat user baru
                # Password di sini None karena login via Google
                new_user = User(username=username, email=email, password=None, role='guest', google_id=google_user_id)
                db.session.add(new_user)
                db.session.commit()
                user = new_user
                current_app.logger.info(f"New user {user.username} registered via Google.")

        # Buat JWT tokens
        access_token = create_access_token(identity=user.id, additional_claims={"role": user.role})
        refresh_token = create_refresh_token(identity=user.id)
        
        return access_token, refresh_token, user, None # Return None untuk error_message

    except ValueError as e:
        # Token tidak valid
        current_app.logger.warning(f"Invalid Google ID Token: {e}")
        return None, None, None, "Invalid Google ID Token."
    except Exception as e:
        # Error lain saat verifikasi atau operasi DB
        current_app.logger.error(f"Error during Google authentication: {e}", exc_info=True)
        return None, None, None, "Internal server error during Google authentication."


def get_user_by_id(user_id):
    """
    Mengambil objek User berdasarkan ID.
    Args:
        user_id (int): ID pengguna.
    Returns:
        User: Objek User jika ditemukan, None jika tidak.
    """
    return User.query.get(user_id)

def update_user(user_id, data):
    """
    Memperbarui data pengguna berdasarkan ID.
    Args:
        user_id (int): ID pengguna yang akan diperbarui.
        data (dict): Data yang akan diperbarui (username, email, password, role, nik).
    Returns:
        User: Objek User yang sudah diperbarui jika berhasil, None jika user tidak ditemukan.
        str: Pesan error jika ada konflik (username/email/NIK sudah ada).
    """
    user = User.query.get(user_id)
    if not user:
        return None, "User not found."

    # Periksa konflik username jika username diupdate
    if 'username' in data and data['username'] != user.username:
        if User.query.filter_by(username=data['username']).first():
            return None, "Username already exists."
        user.username = data['username']

    # Periksa konflik email jika email diupdate
    if 'email' in data and data['email'] != user.email:
        if User.query.filter_by(email=data['email']).first():
            return None, "Email already exists."
        user.email = data['email']

    # Periksa konflik NIK jika NIK diupdate
    if 'nik' in data and data['nik'] != user.nik:
        if data['nik'] and User.query.filter_by(nik=data['nik']).first():
            return None, "NIK already exists."
        user.nik = data['nik']

    # Perbarui password jika diberikan
    if 'password' in data and data['password']:
        user.set_password(data['password'])
    
    # Perbarui role jika diberikan
    if 'role' in data:
        user.role = data['role']

    db.session.commit()
    return user, None

