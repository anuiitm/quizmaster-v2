from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from backend.models.model import User
from backend.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    qualification = data.get('qualification')
    dob_str = data.get('dob')
    dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email already registered'}), 409 
    hashed_pw = generate_password_hash(password)
    new_user = User(
        email=email,
        password=hashed_pw,
        full_name=full_name,
        qualification=qualification,
        dob=dob,
        is_admin=False
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': f'Registration successful! Welcome {full_name}! You can now login with your email and password.'}), 201
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({
            'message': 'Login successful',
            'is_admin': user.is_admin,
            'full_name': user.full_name
        }), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200
@auth_bp.route('/test', methods=['GET'])
def test():
    return {'message': 'auth works'}
