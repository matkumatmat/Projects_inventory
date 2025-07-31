# --- backend/run.py ---
# Layer: Application Entry Point

import os
from app import create_app # Import fungsi factory create_app dari package 'app'
from app.utils.extensions import db # Import instance db dari ekstensi
from flask_migrate import Migrate # Import Migrate (sudah diinisialisasi di extensions)
from dotenv import load_dotenv # Untuk memuat environment variables dari .env

load_dotenv()

config_name = os.getenv('FLASK_ENV', 'development')

app = create_app(config_name)

migrate = Migrate(app, db) # Pastikan migrate diinisialisasi dengan app dan db

# Jika Anda ingin menambahkan command CLI kustom, bisa ditambahkan di sini
# Contoh:
# @app.cli.command('seed-db')
# def seed_db_command():
#     """Menambahkan data dummy ke database."""
#     # Logika untuk menambahkan data dummy
#     print("Database seeded!")

if __name__ == '__main__':
    app.run()

