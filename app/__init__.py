# --- backend/app/__init__.py ---
import os
from flask import Flask
from .utils.config import config_by_name
from .utils.extensions import db, migrate, bcrypt, cors, jwt, ma
from .error_handler.errors import register_error_handlers # Import fungsi error handler kita
import logging # Import modul logging
from logging.handlers import RotatingFileHandler # Import untuk log ke file

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])

    # Inisialisasi ekstensi dengan aplikasi Flask
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    cors.init_app(app)
    jwt.init_app(app)
    ma.init_app(app)

    # --- Konfigurasi Logging ke File (error_log.log) ---
    # Konfigurasi ini hanya akan aktif saat aplikasi TIDAK dalam mode debug dan TIDAK dalam mode testing.
    # Ini ideal untuk lingkungan production.
    if not app.debug and not app.testing:
        # Pastikan folder 'logs' ada. Jika belum, buat.
        if not os.path.exists('error_handler'):
            os.mkdir('error_handler')
        
        # Buat handler untuk menulis log ke file 'error_log.log'.
        # RotatingFileHandler akan membuat file log baru setelah mencapai ukuran tertentu (100 MB)
        # dan menyimpan hingga 10 file backup.
        file_handler = RotatingFileHandler('error_handler/error_log.log', maxBytes=1024 * 1024 * 100, backupCount=10)
        
        # Atur format pesan log.
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Atur level logging untuk file handler. Hanya pesan dengan level ERROR atau lebih tinggi yang akan ditulis ke file.
        file_handler.setLevel(logging.ERROR) 

        # Tambahkan file handler ini ke logger aplikasi Flask.
        app.logger.addHandler(file_handler)
        
        # Atur level logging keseluruhan untuk aplikasi.
        # Ini berarti app.logger akan memproses pesan INFO, WARNING, ERROR, CRITICAL.
        # Namun, hanya yang ERROR ke atas yang akan ditulis ke file_handler.
        app.logger.setLevel(logging.WARNING)
        
        # Opsional: Jika Anda ingin juga melihat log di konsol saat production (misal di Docker logs),
        # Anda bisa menambahkan StreamHandler juga, atau pastikan environment production Anda
        # menangani output stdout/stderr dari Gunicorn.
        
    # --- Mendaftarkan Error Handlers ---
    register_error_handlers(app)

    # --- Registrasi Blueprints (contoh, sesuaikan dengan blueprint Anda) ---

    from .blueprints.auth.routes import auth_bp
    app.register_blueprint(auth_bp)
    from .blueprints.admin.inbound.routes import inbound_bp
    app.register_blueprint(inbound_bp)
    from .blueprints.admin.view.routes import stock_view_bp
    app.register_blueprint(stock_view_bp)

    # from .blueprints.common.routes import common_bp
    # app.register_blueprint(common_bp)
    # from .blueprints.guest.routes import guest_bp
    # app.register_blueprint(guest_bp)
    # from .blueprints.admin.routes import admin_bp
    # app.register_blueprint(admin_bp)
    # from .blueprints.superadmin.routes import superadmin_bp
    # app.register_blueprint(superadmin_bp)

    return app