# app/extensions.py 
# Layer: Konfigurasi
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

# --- PERBAIKAN: Tambahkan Konvensi Penamaan untuk Alembic/SQLite ---
# Ini akan secara otomatis membuat nama untuk constraint (seperti foreign key)
# dan menyelesaikan error 'Constraint must have a name'.
from sqlalchemy import MetaData
naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
metadata = MetaData(naming_convention=naming_convention)
# ----------------------------------------------------------------

# PERBAIKAN: Gunakan metadata yang sudah kita definisikan
db = SQLAlchemy(metadata=metadata)
migrate = Migrate()
bcrypt = Bcrypt()
cors = CORS()
jwt = JWTManager()
ma = Marshmallow()
