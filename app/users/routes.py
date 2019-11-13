from flask import Blueprint, jsonify, request
from flask_restplus import Resource, Api, reqparse, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_cors import cross_origin, CORS

from app.auth.models import BlacklistToken
from app.users.models import User
from app import db, jwt

import os
from dotenv import load_dotenv
load_dotenv(verbose=True)

users_bp = Blueprint('users', __name__)
api = Api(users_bp)
CORS(users_bp)

import boto3, botocore

# args = reqparse.RequestParser()
# args.add_argument('username', type=str, required=True, help="The field 'username' cannot be left blank")
# args.add_argument('password', type=str, required=True, help="The field 'password' cannot be left blank")
# args.add_argument('name', type=str, required=True, help="The field 'name' cannot be left blank")
# args.add_argument('email', type=str, required=True, help="The field 'email' cannot be left blank")

user_api_model = api.model('User', {
    'username': fields.String,
    'name': fields.String,
    'email': fields.String
})


@api.route('/list')
class Users(Resource):
    @api.marshal_with(user_api_model)
    def get(self):
        users = User.query.all()
        return users


@api.route('/profile/<username>')
class Profile(Resource):
    @api.marshal_with(user_api_model)
    def get(self, username):
        user = User.query.filter_by(username=username).first()
        return user

S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_KEY = os.getenv("S3_ACCESS_KEY")
S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

s3 = boto3.client(
   "s3",
   aws_access_key_id=S3_KEY,
   aws_secret_access_key=S3_SECRET  
)
def upload_file_to_s3(file, bucket_name, acl="public-read"):
    print(file, bucket_name)
    try:
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
        return f'{S3_LOCATION}{file.filename}'
    except Exception as e:
        # This is a catch all exception, edit this part to fit your needs.
        print("Something Happened: ", e)
        return e

@api.route('/edit')
class Upload(Resource):
    @jwt_required
    @cross_origin()
    def post(self):
        print(request.headers)
        data = {**request.form}        
        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        user.name = data['name']
        user.username = data['username']
        user.email = data['email']
        try:
            user.save()
            return {'Status': 'Ok'}, 200
        except Exception as e:
            return {'Status': 'Fail', 'Message': e}, 500
        else:
            return {'Status': 'Fail'}, 400

@api.route('/upload')
class Upload(Resource):
    @jwt_required
    def post(self):
        S3_BUCKET = os.getenv('S3_BUCKET_NAME')
        S3_KEY = os.getenv("S3_ACCESS_KEY")
        S3_SECRET = os.getenv("S3_SECRET_ACCESS_KEY")
        S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)
        data = request.files
        filename = data['file'].filename
        img_url = upload_file_to_s3(data['file'],S3_BUCKET)

        username = get_jwt_identity()
        print(username)
        user = User.query.filter_by(username=username).first()
        user.profile = img_url
        print(user)
        user.save()
        return {'Status': 'Ok', 'URL':img_url}, 200