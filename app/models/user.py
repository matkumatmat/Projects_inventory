# --- backend/app/models/user.py ---
# Layer: Database Models

from datetime import datetime
from app.utils.extensions import db, bcrypt # Import db dan bcrypt dari ekstensi kita

class User(db.Model):
    """
    Model Database untuk Pengguna (User).
    Mewakili tabel 'users' di database.
    """
    __tablename__ = 'users' # Nama tabel di database

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True) # Password bisa nullable jika login hanya via OAuth
    role = db.Column(db.String(50), nullable=False, default='guest') # Contoh: 'guest', 'admin', 'superadmin'
    
    # --- Tambahan untuk Google OAuth ---
    google_id = db.Column(db.String(255), unique=True, nullable=True) # ID unik dari Google
    
    # --- Tambahan untuk NIK (Nomor Induk Karyawan) ---
    # NIK adalah ID unik dari perusahaan, bisa nullable jika ada user non-karyawan (misal guest)
    nik = db.Column(db.String(50), unique=True, nullable=True) 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, username, email, password=None, role='guest', google_id=None, nik=None):
        """
        Konstruktor untuk membuat objek User baru.
        Password akan otomatis di-hash jika diberikan.
        """
        self.username = username
        self.email = email
        if password: # Hanya set password jika diberikan (untuk login manual)
            self.set_password(password)
        self.role = role
        self.google_id = google_id
        self.nik = nik

    def set_password(self, password):
        """
        Mengatur password pengguna dengan melakukan hashing menggunakan Bcrypt.
        """
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        """
        Memverifikasi password yang diberikan dengan password hash yang tersimpan.
        """
        if self.password_hash: # Hanya cek jika password_hash ada
            return bcrypt.check_password_hash(self.password_hash, password)
        return False # Tidak ada password hash untuk dicocokkan

    def __repr__(self):
        """
        Representasi string dari objek User (berguna untuk debugging).
        """
        return f'<User {self.username} (Role: {self.role})>'

