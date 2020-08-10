#import packages
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

#store the username and email from the input information
#use validators to check the input format
class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    #check if the username is already taken via query
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    #check if the username is already taken via query
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


#check if the info of the user input is valid for these formats via serveral validators
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #remember me checkbox and submit button
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#check if the user input is valid via several validators. then rewrite the user data regarding the input.
class UpdateAccountForm(FlaskForm):
    #validate if the username has a length of 2-20 characters.
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    #validate if the email is an valid email address.
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    #validate if the extension name of the picture is jpg or png.
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')
    #validate the username, check if the new username matches the record via query.
    def validate_username(self, username):
        #if not match, store the input as the new username
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            #if match, give an error message.
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    #
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


#post form, including title input, content input, and submit button.
class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')