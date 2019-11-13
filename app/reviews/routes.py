from flask import Blueprint, jsonify, request
from flask_restplus import Resource, Api, reqparse, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.reviews.models import Review
from app.users.models import User 

import requests
from dotenv import load_dotenv
load_dotenv(verbose=True)

reviews_bp = Blueprint('reviews',__name__)
api = Api(reviews_bp)
import os

from flask_cors import CORS
CORS(reviews_bp)
GOOGLE_API_KEY=os.getenv('GOOGLE_API_KEY')

review_model = api.model('Review',{
    'title': fields.String,
    'description': fields.String,
    'isbn': fields.String,
    'id': fields.Integer,
    'author_name': fields.String(attribute='author.name'),
    'author_username': fields.String(attribute='author.username'),
    'author_profile': fields.String(attribute='author.profile'),
    'user_id': fields.Integer,
    'created':  fields.DateTime(dt_format='rfc822')
})

create_model = api.model('Create',{
    'title': fields.String,
    'description': fields.String,
    'isbn': fields.String
})

book_model = api.model('Book',{
    'title': fields.String,
    'subtitle': fields.String,
    'authors': fields.String,
    'description': fields.String,
    'pageCount': fields.String,
    'averageRating': fields.String,
    'thumbnail': fields.String
})

@api.route('/book')
class Book(Resource):
    def get(self):
        return {'book': False, 'loading': True},200

@api.route('/book/<isbn>')
class Books(Resource):
    def get(self, isbn):
        response = requests.get(f'https://www.googleapis.com/books/v1/volumes?q={isbn}&key={GOOGLE_API_KEY}')
        book = response.json()        
        bookItem =  book['items'][0]
        if bookItem:
            volumeInfo = bookItem['volumeInfo']
        else:
            return []
            
        if volumeInfo:
            title = volumeInfo.get('title')
            subtitle = volumeInfo.get('subtitle')
            authors = volumeInfo.get('authors')
            description = volumeInfo.get('description')
            pageCount = volumeInfo.get('pageCount')
            averageRating = volumeInfo.get('averageRating')
            imageLink = volumeInfo.get('imageLinks')
            if imageLink:
                thumbnail = imageLink.get('thumbnail')
            else:
                thumbnail = None

            if volumeInfo.get('industryIdentifiers') is not None:
                type_0 = volumeInfo.get('industryIdentifiers')[0].get('type')   
                if type_0 == 'ISBN_13':
                    isbn_13 = volumeInfo.get('industryIdentifiers')[0].get('identifier')
                    isbn_10 = volumeInfo.get('industryIdentifiers')[1].get('identifier')
                else:
                    isbn_13 = volumeInfo.get('industryIdentifiers')[1].get('identifier')
                    isbn_10 = volumeInfo.get('industryIdentifiers')[0].get('identifier')
            else:
                isbn_13, isbn_10 = None, None
            info = {
                'title': title,
                'subtitle': subtitle,
                'authors': authors,
                'description': description,
                'pageCount': pageCount,
                'averageRating': averageRating,
                'thumbnail': thumbnail,
                'isbn_13': isbn_13,
                'isbn_10': isbn_10,
                'loading': False
            }

            return info
        else:
            return []

    def options(self, isbn):
        return {'asdhsadasd': 'dnasid'}

@api.route('/list/<isbn>')
class Reviews(Resource):
    @api.marshal_with(review_model)
    def get(self, isbn):
        reviews = Review.query.filter_by(isbn=isbn)\
            .order_by(Review.created.desc()).all()
        return reviews
        
@api.route('/register', methods=['GET','POST'])
@api.header('Authorization: Bearer', 'JWT TOKEN', required=True)
class ReviewRegister(Resource):
    @api.expect(create_model)
    @jwt_required
    def post(self):
        data = request.json

        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        review_data = {
            **data,
            'user_id': user.id
        }        

        try:
            review = Review(**review_data) 
            review.save()
            return {'Status': 'Ok', 'Message': 'Review created successfully!', 
                    'review': review_data}, 201
        except Exception as e:
            return {'Message': str(e)}, 500

    @jwt_required
    def options(self):
        data = request.json

        username = get_jwt_identity()
        user = User.query.filter_by(username=username).first()
        
        review_data = {
            **data,
            'user_id': user.id
        }        

        try:
            review = Review(**review_data) 
            review.save()
            return {'Status': 'Ok', 'Message': 'Review created successfully!', 
                    'review': review_data}, 201
        except Exception as e:
            return {'Message': str(e)}, 500


        