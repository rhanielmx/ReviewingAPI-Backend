from flask import Blueprint, request, after_this_request
from flask_restplus import Resource, Api, reqparse, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_raw_jwt, get_jti
from flask_cors import cross_origin, CORS

import flask_jwt_extended

from app.users.models import User
from app.auth.models import BlacklistToken
from app import db, jwt

import datetime, requests

auth_bp = Blueprint('auth',__name__)
api = Api(auth_bp)

from flask_bcrypt import generate_password_hash, check_password_hash


user_login_model = api.model('UserLogin', {
    'username': fields.String,
    'password': fields.String
})

create_model = api.model('Create',{
    'name': fields.String,
    'email': fields.String,
    'username': fields.String,
    'password': fields.String,
    'password_confirm': fields.String
})


@api.route('/register', methods=['GET','POST'])
class UserRegister(Resource):
    @api.expect(create_model)
    def post(self):
        data = request.json

        if data['password'] != data['confirm_password']:
            return {'Message': 'Different passwords!'}, 400
        
        if User.query.filter_by(username=data['username']).first() is not None:
            return {'Message': 'User already exists!'}, 400        

        user_data = {
            'name': data['name'],
            'email': data['email'],
            'username': data['username'],
            'password': data['password']
        }

        print(user_data)

        try:
            user = User(**user_data)     
            user.save()
            return {'Status':'Ok','Message': 'User created successfully!', 'user': user.json()}, 201, {'Access-Control-Allow-Origin': '*'}
        except Exception as e:
            print(str(e))
            return {"Status":"Fail", "Message": str(e)}
      
        
@api.route('/login', methods=['GET','POST'])
class UserLogin(Resource):
    @api.expect(user_login_model)
    def post(self):
        data = request.json
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            access_token = create_access_token(identity=user.username,\
                                                expires_delta=datetime.timedelta(days=1))
            payload = {**user.json(), 'token': access_token}
            return {'Status': 'ok', 'Message': 'Logged in', 'user': payload},\
                 200, {'Access-Control-Allow-Origin': '*'}
        return {'Status': 'fail', 'Message': 'Not logged in'}, 400, {'Access-Control-Allow-Origin': '*'}

@api.route('/logout', methods=['POST'])
class UserLogout(Resource):
    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti']
        blacklist_token = BlacklistToken(jwt_id)
        try:
            db.session.add(blacklist_token)
            db.session.commit()
            return {'Status': "Success", "Message": "Successfully Logged Out"}, 200
        except Exception as e:
            print('except')
            return {"Status":"Fail", "Message": str(e)}, 400

token_model = api.model('Token',{
    'token': fields.String
})

@api.route('/validateToken', methods=['POST','OPTIONS'])
class Validate(Resource):    
    @cross_origin()
    @jwt_required
    def post(self):
        data = request.headers
        jwt = data['Authorization'].split(' ')[-1]
        jti = get_jti(jwt)
       

        valid = not BlacklistToken.check_blacklist(jti)
        return {'Status': 'Ok', 'valid': valid}, 200

    @cross_origin()
    @jwt_required
    def options(self):
        data = request.headers
        jwt = data['Authorization'].split(' ')[-1]
        jti = get_jti(jwt)
        valid = not BlacklistToken.check_blacklist(jti)
        return {'Status': 'Ok', 'valid': valid}, 200    