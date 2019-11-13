from app import db
import datetime

class Review(db.Model):
    __tablename__ = 'reviews'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String)
    title = db.Column(db.String(80))
    description = db.Column(db.String(300))
    created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()

    def _init__(self, title, description, isbn, user_id):
        self.title = title
        self.description = description
        self.isbn = isbn
        self.user_id = user_id

    def __repr__(self):
        return f'Review: {self.title}'