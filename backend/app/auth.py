from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
)
from .models import db, AuthUser
from flask_bcrypt import Bcrypt
from .extensions import limiter   # Flask-Limiter instance

bcrypt = Bcrypt()
auth_bp = Blueprint('auth', __name__)


# ─── POST /api/auth/register ──────────────────────────────────────────────────
@auth_bp.route('/register', methods=['POST'])
@limiter.limit("3 per minute")           # prevent account creation spam
def register():
    """Create a new account with email + password."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Basic validation
    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400
    if len(password) < 6:
        return jsonify({'status': 'error', 'message': 'Password must be at least 6 characters.'}), 400
    if '@' not in email:
        return jsonify({'status': 'error', 'message': 'Invalid email address.'}), 400

    # Check for existing account
    if AuthUser.query.filter_by(email=email).first():
        return jsonify({'status': 'error', 'message': 'An account with this email already exists.'}), 409

    # Hash the password and save user
    pw_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = AuthUser(email=email, password_hash=pw_hash)
    db.session.add(new_user)
    db.session.commit()

    # Issue tokens immediately so user is logged in right after registering
    access_token = create_access_token(identity=str(new_user.id))
    refresh_token = create_refresh_token(identity=str(new_user.id))

    return jsonify({
        'status': 'success',
        'message': 'Account created.',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': new_user.to_dict()
    }), 201


# ─── POST /api/auth/login ─────────────────────────────────────────────────────
@auth_bp.route('/login', methods=['POST'])
@limiter.limit("5 per minute")           # brute-force protection
def login():
    """Authenticate with email + password, return access + refresh tokens."""
    data = request.get_json(silent=True) or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'status': 'error', 'message': 'Email and password are required.'}), 400

    user = AuthUser.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        # Same message for both "user not found" and "wrong password" — prevents enumeration
        return jsonify({'status': 'error', 'message': 'Invalid email or password.'}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        'status': 'success',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }), 200


# ─── POST /api/auth/refresh ───────────────────────────────────────────────────
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Use a valid refresh token to get a new access token."""
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({
        'status': 'success',
        'access_token': new_access_token
    }), 200


# ─── GET /api/auth/me ─────────────────────────────────────────────────────────
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """Return the currently logged-in user's info (used to rehydrate session)."""
    user_id = int(get_jwt_identity())
    user = db.session.get(AuthUser, user_id)
    if not user:
        return jsonify({'status': 'error', 'message': 'User not found.'}), 404
    return jsonify({'status': 'success', 'user': user.to_dict()}), 200
