from app import db
from flask_bcrypt import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String)
    email = db.Column(db.String)
    profile = db.Column(db.String)
    reviews = db.relationship('Review', backref='author', lazy=True)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def json(self):
        return {
            'username': self.username,
            'email': self.email,
            'name': self.name,
            'profile': self.profile
        }

    def __init__(self, username, password, name, email):
        self.username = username
        self.password_hash = generate_password_hash(password).decode('utf8')
        self.name = name
        self.email = email
        self.profile = 'http://www.nationalaquatic.com/wp-content/uploads/2012/11/generic-profile-pic.png'

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'User: {self.name}'