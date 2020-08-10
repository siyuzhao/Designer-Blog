import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('home.html', posts=posts)


@app.route("/about")
def about():
    return render_template('about.html', title='About')

#this function check if the register info is valid, and create new account based on the input
@app.route("/register", methods=['GET', 'POST'])
def register():
    #if the register information is valid, return to home page.
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    #if the input is valid, create new account via db
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        #provide feedback to the users to inform the new account is created
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    #render the 'register.html'page
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
#login function
def login():
    #if the info is authenticated, go to home page
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    #check if username and the password match the record via query. if match, go batck to home page
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        #if not match, flash a warning to inform the user
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    #render 'login.html' page from the templates
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
#help user log out. then go back to the homepage
def logout():
    logout_user()
    return redirect(url_for('home'))


#resize the picture to a 125x125 thumbnail. save it to the picture_path
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

#enable the user to update account information
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    #check if the input of the form is valid
    if form.validate_on_submit():
        #rewrite the record of the userdata(image_file,username,and email) with the new input
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        #commit the change via db.
        db.session.commit()
        #give a feedback and go back to the account page.
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    #render 'account.html' page
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)

#let the user create a new post
@app.route("/post/new", methods=['GET', 'POST'])
#the user has to be logged in
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        #store the input in these 3 variables: title, content, and author. add the new data via db.
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    #render 'create_post.html' page
    return render_template('create_post.html', title='New Post',
                           form=form, legend='New Post')

#when the user click on the post title, redirect them to the post page.
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#function to let the user update a post
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
#the user need to be logged in
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    #check if the current user is also the author of the post
    if post.author != current_user:
        abort(403)
    form = PostForm()
    #change the title and the content of the post regarding the new input. commit the change via db.
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    #render the 'create_post.html' page
    return render_template('create_post.html', title='Update Post',
                           form=form, legend='Update Post')


#function to let the user delete a post
@app.route("/post/<int:post_id>/delete", methods=['POST'])
#the user need to be logged in
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    #check if the current user is also the author of the post
    if post.author != current_user:
        abort(403)
    #commit change via db
    db.session.delete(post)
    db.session.commit()
    #give user a feedback
    flash('Your post has been deleted!', 'success')
    #go back to home page
    return redirect(url_for('home'))

#sort the posts by author
@app.route("/user/<string:username>")
def user_posts(username):
    page = request.args.get('page', 1, type=int)
    #query the posts via username
    user = User.query.filter_by(username=username).first_or_404()
    #maximum of 5 posts per page. list the posts via the time order
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #render 'user_posts.html' page
    return render_template('user_posts.html', posts=posts, user=user)
