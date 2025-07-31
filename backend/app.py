from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect, generate_csrf
from backend.extensions import db, login_manager
from backend.models.model import User
from backend.api.auth import auth_bp
from backend.api.admin import admin_bp
from backend.api.user import user_bp
from backend.config import Config
from werkzeug.security import generate_password_hash
from datetime import date, timezone, timedelta
from flask_wtf.csrf import CSRFError
from backend.utils.performance import performance_middleware
import os
from backend.celery_app import create_celery

# IST timezone (UTC+5:30)
IST = timezone(timedelta(hours=5, minutes=30))

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['WTF_CSRF_HEADERS'] = ['X-CSRFToken']
    app.config['WTF_CSRF_SSL_STRICT'] = False
    
    # Set timezone for the app
    app.config['TIMEZONE'] = 'Asia/Kolkata'
    
    CORS(app,
         supports_credentials=True,
         origins=['http://localhost:5173'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'X-CSRFToken']
    )

    @app.before_request
    def disable_csrf_for_options():
        if request.method == "OPTIONS":
            request.csrf_valid = True
    
    @app.before_request
    def disable_csrf_for_delete():
        if request.method == "DELETE":
            request._csrf_valid = True
            try:
                request.csrf_valid = True
            except:
                pass
    
    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        return jsonify({'message': 'CSRF token missing or invalid'}), 400
    
    @app.errorhandler(400)
    def handle_400_error(e):
        return jsonify({'message': 'Bad request'}), 400
    
    db.init_app(app)
    login_manager.init_app(app)
    
    before_request, after_request = performance_middleware()
    app.before_request(before_request)
    app.after_request(after_request)

    with app.app_context():
        db.create_all()
        if not User.query.filter_by(is_admin=True).first():
            admin_user = User(
                email="admin@quizmaster.com",
                password=generate_password_hash("admin123"),
                full_name="Admin",
                qualification="masters",
                dob=date(1990, 1, 1),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    @app.route('/api/get_csrf_token', methods=['GET'])
    def get_csrf_token():
        return jsonify({'csrf_token': generate_csrf()})

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(user_bp, url_prefix='/api/user')

    @app.route('/ping')
    def ping():
        return jsonify({'message': 'pong'})

    @app.route('/debug/routes')
    def debug_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                'endpoint': rule.endpoint,
                'methods': list(rule.methods),
                'path': str(rule)
            })
        return jsonify(routes)

    return app
