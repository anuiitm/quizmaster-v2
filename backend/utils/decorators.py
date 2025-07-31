from flask import jsonify, g
from flask_login import current_user
from functools import wraps
from backend.utils.cache import rate_limit

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'message': 'Access denied: Admins only'}), 403
        return f(*args, **kwargs)
    return decorated_function

def user_context_middleware(f):
    """Middleware to add user context to Flask g object for caching"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.is_authenticated:
            g.user_id = current_user.id
            g.user_email = current_user.email
            g.is_admin = current_user.is_admin
        else:
            g.user_id = None
            g.user_email = None
            g.is_admin = False
        return f(*args, **kwargs)
    return decorated_function

def secure_endpoint(rate_limit_requests: int = 60):
    """Combined decorator for security: rate limiting + user context"""
    def decorator(f):
        @wraps(f)
        @rate_limit(rate_limit_requests)
        @user_context_middleware
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_secure_endpoint(rate_limit_requests: int = 100):
    """Combined decorator for admin endpoints: admin check + rate limiting + user context"""
    def decorator(f):
        @wraps(f)
        @rate_limit(rate_limit_requests)
        @user_context_middleware
        @admin_required
        def decorated_function(*args, **kwargs):
            return f(*args, **kwargs)
        return decorated_function
    return decorator
