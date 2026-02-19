from functools import wraps
from flask import session, jsonify

def role_required(required_role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if "role" not in session:
                return jsonify({"message": "Unauthorized"}), 401
            
            if session["role"] != required_role:
                return jsonify({"message": "Forbidden"}), 403
            
            return func(*args, **kwargs)
        return wrapper
    return decorator