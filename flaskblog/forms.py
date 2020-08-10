''' import packages '''
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User

#store the username and email from the input information
#use validators to check the input format
class RegistrationForm(FlaskForm):
    ''' this is a class to validate the input and save the data during registration.

    Args:
        validators: serveral validator to check the input. including length validator, email format validator, equal to validator
        
    Attributes:    
        username: form input username
        email: form input email
        password: form input password
    
    Return:
        check if the form input is valid. if valid, then procss validate_username function and validate_email function to check if they are already taken.
        if not taken, return the user data package.


    '''
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
        ''' this is a function to check whether the username is valid.
        Args:
            usesr: input from the user, query by username
            username: stored username data

        Return:
            check if new inputted username equals to username.data, if so, raise error
        '''
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    #check if the username is already taken via query
    def validate_email(self, email):
        ''' this is a function to check whether the email is valid.
        Args:
            usesr: input from the user, query by email
            email: stored email data

        Return:
            check if new inputted email equals to username.data, if so, raise error
        '''
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


#check if the info of the user input is valid for these formats via serveral validators
class LoginForm(FlaskForm):
    ''' this is a class during the login section

    Args:
        validator: in this case, the datarequired validators check if the email and password match the record.
        remember: boolean checkbox
        submit: button

    Attributes:
        email: form input email
        password: form input password

    Return:
        form requries input from the user.
        enable the user to check remember me and then click submit button

    '''
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    #remember me checkbox and submit button
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

#check if the user input is valid via several validators. then rewrite the user data regarding the input.
class UpdateAccountForm(FlaskForm):
    '''this is a form class to enable the user update profile information.

    Args:
        validators: same as the validators in the RegistrationForm class.
        submit: button
    
    Attributes:
        username: form input username
        email: form input email
        picture: form uploaded picture
    
    Return:
        form requires input from the user.
        validator check if the input is valid regariding the format.
        after clicking submit button, check if the input is already taken.

    '''
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
        '''function to check if the username is already taken. explained previously. '''
        #if not match, store the input as the new username
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            #if match, give an error message.
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
    #
    def validate_email(self, email):
        '''function to check if the email is already taken. explained previously.'''
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


#post form, including title input, content input, and submit button.
class PostForm(FlaskForm):
    '''this is a form class to enable the user input a new post.
    
    Args:
        submit: button

    Attributes:
        title: form input title
        content: form input content

    '''
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')