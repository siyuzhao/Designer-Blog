'''import the pre-setup packages'''
import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flaskblog import app, db, bcrypt
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required


#after clicking the home button, redirect to the 'home.html'.
@app.route("/")
@app.route("/home")
def home():
    ''' this is a function used to redirect the users to the homepage. list the posts by order. limit the num of posts by paginate.

    Args:
        page: start from page 1
        posts: query the post data, order them by post.date_posted, max posts per_page=5

    Return:
        render 'home.html' page.
    '''
    page = request.args.get('page', 1, type=int)
    #limit the numbers of posts per page to 5.
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #render the 'home.html'
    return render_template('home.html', posts=posts)


#after clicking the about button, redirect to the 'about.html' page.
@app.route("/about")
def about():
    ''' this is a function used to redirect the users to the about page.

    Return:
        render 'about.html' page.
    '''
    return render_template('about.html', title='About')

#this function check if the register info is valid, and create new account based on the input
@app.route("/register", methods=['GET', 'POST'])
def register():

    ''' this is a function used to fulfill the register function.

    Args:
        form: load the RegistrationForm
        user: data package, including username, email, and password
        hashed_password: use bcrypt to generate a hash for the password

    Return:
        add the user data to the record, commit it by db.
        flash a feedback string.
        render 'register.html' page.
        after registration, render 'login.html' page.
    '''

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

    ''' this is a function used to fulfill the login function.

    Args:
        form: load the LoginForm
        user: data package, including username, email, and password
        user.password: recorded user password
        form.password.data: input of the password section from the form
        next_page: homepage in this case

    Return:
        render 'login.html' page
        load the user data by email via query
        use bcrypt to check if user.password and form.password.data is the same
        if same, flash a feedback string and redirect to 'home.html' page
        if not same, flash a feedback string and stay at the 'login.html' page
    '''

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
    ''' this is a function to enable the user logout and redirect to 'home.html' page.'''
    logout_user()
    return redirect(url_for('home'))


#resize the picture to a 125x125 thumbnail. save it to the picture_path
def save_picture(form_picture):
    ''' this is a function to save the uploaded image to a thumbnail.

    Args:
        random_hex, _, f_ext: load the picture file from the form, split its name by fil true ename and file extension name
        picture_fn: recreate the new file name by adding these 2 names together
        picture_path: the path for the new picture file
        output_size: the size of the thumbnail
        i: open the image

    Return:
        save the picture to the path
        resize the picture to 125x125
        resave the picture to the path
    '''
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
    '''this is a function to enable the users update the account information

    Args:
        form: load the UpdateAccountForm here
        form.username.data: username input from the form
        form.email.data: email input from the form
        picture_file: save the uploaded picture file
        current_user.image: user profile image in the record
        current_user.name: username in the record
        current_user.email: user email in the record
        request.method
    Return:
        render 'account.html' page
        resave the user data from the input form
        commit the change via db.

    '''
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
    ''' this is a function to enable the user to create new post.

    Args:
        form: load PostForm here
        post: data package including title, content, and author
    
    Return:
        render 'create_post.html' page
        save the title.date, content.date, and current_user from the form as the title, conten, and author of variable post
        commit the change via db.
        flash out a string
        redirect to the 'home.html' page.
    '''

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
    ''' this is a function to display the post.

    Args:
        post: data package, get the post by query its id.

    Return:
        render 'post.html' page.
    
    '''
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)

#function to let the user update a post
@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
#the user need to be logged in
@login_required
def update_post(post_id):
    ''' this is a function to update the existing post.

    Args:
        post: data package, get the post by query its id. including title, content.
        form: load PostForm here.
        form.xxx.data: the input data from the form

    Return:
        render ‘create_post.html’ page
        rewrite the post.data by the input from the form
        commit the changes via db.
        flash out a string as feedback
        redirect to 'post.html' page.

    '''
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
    '''this is a function to delete the post.
    Args:
        post: data package, get the post by query its id. including title, content, author.
    
    Return:
        commit the delete via db.
        flash out a string as feedback.
        redirect to 'home.html' page.
    '''
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
    ''' this is a function to sort the posts by author.
    
    Args：
        page: start from page 1
        user: user data. here query the user data by username
        posts: post data package. here query the posts by author. order the posts by date_posted. limit the num per_page by paginate.
    
    Return:
        query the posts by author
        redirect to the 'user_posts.html' page
    '''
    page = request.args.get('page', 1, type=int)
    #query the posts via username
    user = User.query.filter_by(username=username).first_or_404()
    #maximum of 5 posts per page. list the posts via the time order
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    #render 'user_posts.html' page
    return render_template('user_posts.html', posts=posts, user=user)
