# app/errors.py 
# --- backend/app/errors.py ---
# Layer: Konfigurasi Error Handling

from flask import jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException # Import HTTPException untuk menangani error HTTP bawaan Flask
import logging # Import modul logging (meskipun konfigurasi utama ada di __init__.py)

def register_error_handlers(app):
    """
    Mendaftarkan error handler terpusat ke aplikasi Flask.
    Fungsi ini akan dipanggil di create_app() di app/__init__.py.
    """

    # Handler untuk Marshmallow Validation Errors (HTTP 400 Bad Request)
    @app.errorhandler(ValidationError)
    def handle_marshmallow_validation(err):
        """
        Menangkap error validasi dari Marshmallow.
        Ini terjadi ketika data JSON yang masuk tidak sesuai dengan skema yang didefinisikan.
        """
        # Pesan error dari Marshmallow bisa bertingkat, kita buat flat agar mudah dibaca klien.
        messages = {}
        for field, errors in err.messages.items():
            # Ambil pesan error pertama untuk setiap field jika ada beberapa error
            messages[field] = errors[0] if isinstance(errors, list) else errors

        # Log error validasi sebagai peringatan (WARNING)
        # app.logger akan otomatis menulis ke handler yang sudah dikonfigurasi (misal ke file error_log.log)
        app.logger.warning(f"Validation error: {messages}")
        return jsonify(msg="Validation error", errors=messages), 400

    # Handler untuk HTTPException (misalnya 404, 400, 401, 403 yang di-raise Flask)
    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        """
        Menangani error HTTP bawaan Flask seperti 404 Not Found, 400 Bad Request,
        401 Unauthorized, 403 Forbidden, 405 Method Not Allowed, dll.
        Ini mencakup error yang di-raise dengan flask.abort().
        """
        # Log error HTTP sebagai peringatan (WARNING)
        app.logger.warning(f"HTTP Exception: {err.code} - {err.description}")
        return jsonify(msg=err.description), err.code

    # Handler untuk semua error lain yang tidak ditangani secara spesifik (HTTP 500 Internal Server Error)
    @app.errorhandler(Exception)
    def handle_generic_exception(err):
        """
        Menangkap semua error Python lain yang tidak ditangani secara spesifik.
        Ini mencegah bocornya detail internal ke klien dan memastikan error di-log
        dengan traceback lengkap untuk debugging.
        """
        # Penting: Log error yang sebenarnya dengan traceback lengkap (exc_info=True).
        # app.logger akan otomatis menulis ke handler yang sudah dikonfigurasi (misal ke file error_log.log).
        app.logger.error(f"An unhandled exception occurred: {err}", exc_info=True)

        # Kirim respons generik ke klien.
        # Di production, jangan tampilkan detail error yang sensitif ke user.
        # Saat debugging, kita bisa tampilkan detail error untuk kemudahan pengembangan.
        if app.debug: # app.debug akan True jika di DevelopmentConfig
            response = jsonify(msg="An internal server error occurred.", error_detail=str(err))
        else: # Saat production
            response = jsonify(msg="An internal server error occurred.")
        
        return response, 500

