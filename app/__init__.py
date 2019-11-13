from flask import Flask, jsonify
from flask_restplus import Api
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_cors import CORS

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
Migrate(app, db)
jwt = JWTManager(app)
bcrypt = Bcrypt(app)
CORS(app, resources=r'*')

from app.auth.models import BlacklistToken

@jwt.token_in_blacklist_loader
def verify_blacklist(token):
    return BlacklistToken.check_blacklist(token['jti'])

@jwt.revoked_token_loader
def invalided_access_token():
    return jsonify({'message': 'You have been logged out.'}), 401


from app.users.routes import users_bp
from app.reviews.routes import reviews_bp
from app.auth.routes import auth_bp

app.register_blueprint(users_bp, url_prefix='/users')
app.register_blueprint(reviews_bp, url_prefix='/reviews')
app.register_blueprint(auth_bp, url_prefix='/auth')
