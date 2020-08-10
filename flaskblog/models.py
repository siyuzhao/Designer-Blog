'''import packages'''
from datetime import datetime
from flaskblog import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    '''this is a functin to load the user data package by user_id'''
    return User.query.get(int(user_id))

#userdata class. including 
class User(db.Model, UserMixin):
    '''this is the user data class

    Attributes:
        username: user name got from the input
        email: user email got from the input
        image_file: user image got from the input. if not uploaded, use the default.jpg
        password: user password got from the input
        posts: user post, query from the author variable by username

    '''
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    posts = db.relationship('Post', backref='author', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


#Post package, including title, date_posted, content, and user_id.
class Post(db.Model):
    '''this is the post data class

    Attributes:
        title: post title from the input
        date_posted: generated from datetime.utcnow
        content: post content from the input
        user_id: current user.id
    
    '''

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}')"