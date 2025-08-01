# --- backend/app/blueprints/auth/schemas.py ---
# Layer: API Schemas

from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    """
    Skema untuk validasi data registrasi pengguna baru.
    """
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    password = fields.String(required=True, validate=validate.Length(min=6))
    role = fields.String(validate=validate.OneOf(['guest', 'admin', 'superadmin']), load_default='guest')
    nik = fields.String(required=False, validate=validate.Length(max=50)) # NIK bisa opsional saat registrasi manual

class UserLoginSchema(Schema):
    """
    Skema untuk validasi data login pengguna.
    """
    username = fields.String(required=True)
    password = fields.String(required=True)

class GoogleLoginSchema(Schema):
    """
    Skema untuk validasi data login via Google OAuth.
    """
    id_token = fields.String(required=True) # Token yang diterima dari Google Sign-In di frontend

class UserSchema(Schema):
    """
    Skema untuk serialisasi data pengguna yang akan dikirim ke klien.
    Tidak menampilkan password_hash untuk keamanan.
    """
    id = fields.Integer(dump_only=True) # dump_only berarti hanya untuk output
    username = fields.String(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.String(dump_only=True)
    google_id = fields.String(dump_only=True) # Tambahan google_id
    nik = fields.String(dump_only=True) # Tambahkan nik
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserEditSchema(Schema):
    """
    Skema untuk mengedit/update data profile user
    """
    username = fields.String(required=False, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=False, validate=validate.Length(max=120))
    password = fields.String(required=False, validate=validate.Length(min=6)) 
    role = fields.String(validate=validate.OneOf(['guest', 'admin', 'superadmin']), required=False) # Role bisa diupdate
    nik = fields.String(required=False, validate=validate.Length(max=50))