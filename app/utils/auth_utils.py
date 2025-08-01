# app/utils/auth_utils.py
from functools import wraps
from flask_jwt_extended import get_jwt_identity, get_jwt
from flask import jsonify

def roles_required(*roles):
    """
    Decorator untuk membatasi akses ke endpoint berdasarkan role.
    Memastikan pengguna memiliki setidaknya salah satu role yang diperlukan.
    """
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            if user_role not in roles:
                return jsonify(msg="Admins only!"), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
