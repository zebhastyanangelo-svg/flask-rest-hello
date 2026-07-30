"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import jwt
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User

app = Flask(__name__)
app.url_map.strict_slashes = False

# JWT Secret key
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['JWT_ALGORITHM'] = 'HS256'
app.config['JWT_EXPIRATION_DELTA'] = timedelta(hours=24)

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


def generate_token(user_id):
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + app.config['JWT_EXPIRATION_DELTA'],
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, app.config['JWT_SECRET_KEY'], algorithm=app.config['JWT_ALGORITHM'])


def decode_token(token):
    try:
        payload = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=[app.config['JWT_ALGORITHM']])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Body is empty"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already registered"}), 400
    
    user = User(email=email, is_active=True)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    
    token = generate_token(user.id)
    return jsonify({
        "msg": "User created successfully",
        "token": token,
        "user": user.serialize()
    }), 201


@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"msg": "Body is empty"}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid email or password"}), 401
    
    if not user.is_active:
        return jsonify({"msg": "User is deactivated"}), 401
    
    token = generate_token(user.id)
    return jsonify({
        "msg": "Login successful",
        "token": token,
        "user": user.serialize()
    }), 200


@app.route('/api/private', methods=['GET'])
def private():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"msg": "Missing or invalid token"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = decode_token(token)
    
    if not user_id:
        return jsonify({"msg": "Token expired or invalid"}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"msg": "User not found or deactivated"}), 401
    
    return jsonify({
        "msg": "Access granted to private data",
        "user": user.serialize(),
        "secret_data": "This is private data only visible to authenticated users"
    }), 200


@app.route('/api/validate-token', methods=['GET'])
def validate_token():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"valid": False, "msg": "Missing or invalid token"}), 401
    
    token = auth_header.split(' ')[1]
    user_id = decode_token(token)
    
    if not user_id:
        return jsonify({"valid": False, "msg": "Token expired or invalid"}), 401
    
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return jsonify({"valid": False, "msg": "User not found or deactivated"}), 401
    
    return jsonify({
        "valid": True,
        "user": user.serialize()
    }), 200


@app.route('/user', methods=['GET'])
def handle_hello():
    response_body = {
        "msg": "Hello, this is your GET /user response "
    }
    return jsonify(response_body), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
