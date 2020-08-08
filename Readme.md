Description
This project is a blog-based website implemented with Flask. The purpose of this website is to provide a platform enabling product designers & other tech people to post their ideas and thoughts during this social distancing period.
Via this website, the users will be able to post texts regarding news that interests them. They will also be able to view other posts and sort the posts by authors. This will help the users exchange ideas and get further inspiration.
 
Requirement
Python 3.7 or higher
 
Installation
use pip to install the required third party packages as follows (input “pip install xxx” in the terminal):
Flask 1.0 or higher
Flask-Bcrypt 0.5 or higher
Flask-Login 0.4.1 or higher
Flask-Mail 0.9.1 or higher
Flask-SQLAlchemy 2.4.4 or higher
SQLAlchemy 1.3.18 or higher
Bcrypt 5.0.0 or higher
Blinker 1.4 or higher
 
Usage
Run.py: run it in the project root folder by inputting “python run.py” in the terminal, so it can import from the flaskblog folder
Code Examples

# define a ‘user_posts’ function -- after clicking on the username, render to the template ‘user_post.html’
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('user_posts.html', posts=posts, user=user)


# update the saved user.image_file (have to check if the input is a valid image), user.username, and user.email with the new input from the user; commit the changes and flash a sentence to inform the users
if form.picture.data:
picture_file = save_picture(form.picture.data)
current_user.image_file = picture_file
current_user.username = form.username.data
current_user.email = form.email.data
db.session.commit()
flash('Your account has been updated!', 'success')
return redirect(url_for('account'))



#the class ‘LoginForm’will check if the input email and password match the record via utilizing the imported packages.
from wtforms import StringField, PasswordField, SubmitField, BooleanField
class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

Known issues
Currently, the website is not able to let the user post images.
The user is not able to reset their password.
The user is not able to search for a specific post.


Acknowledges
The Flask Mega-Tutorial Part XVI: Full-Text Search: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-full-text-search
Building a Blog App With Flask and Flask-SQLAlchemy: https://github.com/PrettyPrinted/flask_blog


