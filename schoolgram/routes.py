import os
import secrets
from functools import wraps
from flask import render_template, request, url_for, flash, redirect, abort
from schoolgram import app, db, bcrypt
from schoolgram.forms import RegistrationForm, LoginForm, UpdateAccountForm, MessagePostForm, ImagePostForm, CommentForm, BannedWordForm
from schoolgram.models import User, Post, Comment, Like, BannedWord
from flask_login import login_user, current_user, logout_user, login_required

# users can access the home page using the home path or default path
@app.route("/home")
@login_required
def home():
    # Fetch all posts from the database and store them in the posts list
    posts = Post.query.all()
    # Initialise empty list to store the post ids that the current user has like
    liked_post_ids = []
    # Fetch all like instances where the user_id matches the current user's id
    likes = Like.query.filter_by(user_id=current_user.id).all()
    # Appends the post_id of each like instance to the list
    for like in likes:
        liked_post_ids.append(like.post_id)
    # Initialise swapped flag to true
    swapped = True
    while swapped:
        # Reset swapped flag to false before each iteration
        swapped = False
        # Iterate from 1 to the length of the posts list
        for index in range(1, len(posts)):
            # Compare date posted attribute of the current and previous posts
            if posts[index-1].date_posted < posts[index].date_posted:
                # If previous post is older than current post, swap their positions
                temp_post = posts[index-1]
                posts[index-1] = posts[index]
                posts[index] = temp_post
                # Set swapped flag to true to indicate swap was made
                swapped = True
    return render_template("home.html", title="Home", posts=posts, liked_post_ids=liked_post_ids)

# Access the login page with the login route
@app.route("/login", methods=['GET', 'POST'])
@app.route("/", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Creates an instance of the login form
    form = LoginForm()

    # If the form has been submitted and is valid,
    # Flash a login success message and redirect the user to the home page
    if form.validate_on_submit():
        # Query the database for a user with the provided email address
        user = User.query.filter_by(email=form.email.data).first()
        # If a user with the email exists and the provided password matches the hashed password,
        # the user is logged in
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            # Logs in and creates a user session
            login_user(user)
            # Retrieves 'next' query parameter and redirects to it if it exists
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    # Render the login template with the form instance
    return render_template("login.html", title="login", form=form)

# Access the register page with the register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    # Creates an instance of the registration form
    form = RegistrationForm()

    # If the form has been submitted and is valid,
    # Flash an account created success message and redirect the user to the home page
    if form.validate_on_submit():
        # Generates hashed password using provided password
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        # Will create a new user with the provided credentials and add them to the data base
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created', 'success')
        # Redirect user to the login page after a successful login
        return redirect(url_for('login'))

    # Render the register template with the form instance
    return render_template("register.html", title="register", form=form)

@app.route("/logout")
def logout():
    # Logs out the current user and clears their session data
    logout_user()
    # Redirects to the login page after logging out
    return redirect(url_for('login'))

def save_profile_picture(form_picture):
    # Generates random 8-byte hexadecimal string
    random_hex = secrets.token_hex(8)
    # Extracts file extension from uploaded image's filename
    _, f_ext = os.path.splitext(form_picture.filename)
    # Concatenates random hexadecimal string with file extension to create a new unique file name
    picture_fn = random_hex + f_ext
    # Constructs the file path where the profile picture will be saved
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    # Saves uploaded image file to specified file path
    form_picture.save(picture_path)

    prev_picture = os.path.join(app.root_path, 'static/profile_pics', current_user.image_file)
    # Checks if profile picture exists on the server and removes it
    # Default profile picture will be ignored
    if os.path.exists(prev_picture) and current_user.image_file != 'default.jpg':
        os.remove(prev_picture)

    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # Creates and instance of the Update Account Form
    form = UpdateAccountForm()
    # Updates the username of the current user and commits changes to the database if form data is valid
    if form.validate_on_submit():
        # Checks if user has uploaded new profile picture through the form
        if form.picture.data:
            # Calls the save_profile_picture function which will return the unique file name
            picture_file = save_profile_picture(form.picture.data)
            # Updates the users image file with the new file name
            current_user.image_file = picture_file
        current_user.username = form.username.data
        db.session.commit()
        flash('Your account has been updated', 'success')
        return redirect(url_for('account'))
    # Sets the default value of the username field to the current user's username if the request was a GET method
    elif request.method == 'GET':
        form.username.data = current_user.username
    # Creates a URL for the profile image
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    # Renders the account.html file with the given title and image file
    return render_template("account.html", title="Account", image_file=image_file, form=form)

def teacher_required(route_function):
    # Preserves the meta data of the original route function
    @wraps(route_function)
    # Defines function that accepts any number of positional and keyword arguments
    def decorated_function(*args, **kwargs):
        # Checks if the current user is authenticated and has a role of teacher
        if current_user.is_authenticated and current_user.role == 'teacher':
            # Calls the original route function with the given arguments
            return route_function(*args, **kwargs)
        else:
            # Will display an error message and redirect to the home page
            flash('You must be logged in as a teacher to access this page', 'danger')
            return redirect(url_for('home'))
    return decorated_function

def save_post_image(form_image):
    # Generates random 8-byte hexadecimal string
    random_hex = secrets.token_hex(8)
    # Extracts file extension from uploaded image's filename
    _, f_ext = os.path.splitext(form_image.filename)
    # Concatenates random hexadecimal string with file extension to create a new unique file name
    image_fn = random_hex + f_ext
    # Constructs the file path where the image file will be saved
    image_path = os.path.join(app.root_path, 'static/post_images', image_fn)
    # Saves uploaded image file to specified file path
    form_image.save(image_path)

    return image_fn

@app.route("/create_post", methods=['GET', 'POST'])
@login_required
@teacher_required
def create_post():
    # Instantiates the message and image forms
    message_form = MessagePostForm()
    image_form = ImagePostForm()

    # Checks if the message form has been submitted and is valid
    if message_form.validate_on_submit() and message_form.post_type.data == 'message_post':
        message_post = Post(message=message_form.message.data, post_type='message_post', user=current_user)
        db.session.add(message_post)
        db.session.commit()
        # Prompts the user their message has been posted
        flash('Your message has been posted', 'success')
        return redirect(url_for('home'))

    # Checks if the image form has been submitted and is valid
    if image_form.validate_on_submit() and image_form.post_type.data == 'image_post':
        # Saves the uploaded image file to the server
        image_file = save_post_image(image_form.image.data)
        # Create image post object with users input
        image_post = Post(image_file=image_file, caption=image_form.caption.data, post_type='image_post', user=current_user)

        # Add image post to the database session and commit the changes
        db.session.add(image_post)
        db.session.commit()

        # Prompts the user their image has been posted
        flash('Your image has been posted', 'success')
        return redirect(url_for('home'))
    return render_template('create_post.html', title='Create Message Post', message_form=message_form, image_form=image_form)

# Route expects integer parameter of post_id
@app.route("/post/<int:post_id>", methods=['GET', 'POST'])
@login_required
def post(post_id):
    # Creates an instance of the comment form
    form = CommentForm()

    # Queries the database for a post object with the given post_id
    # Raises a 404 error if the post with that ID is not found
    post = Post.query.get_or_404(post_id)
    # Fetch the comments with post ID of the post from the database and store them in the comments list
    comments = Comment.query.filter_by(post_id=post.id).all()
    # Initialise swapped flag to true
    swapped = True
    while swapped:
        # Reset swapped flag to false before each iteration
        swapped = False
        # Iterate from 1 to the length of the posts list
        for index in range(1, len(comments)):
            # Compare date posted attribute of the current and previous posts
            if comments[index - 1].date_posted < comments[index].date_posted:
                # If previous post is older than current post, swap their positions
                temp_post = comments[index - 1]
                comments[index - 1] = comments[index]
                comments[index] = temp_post
                # Set swapped flag to true to indicate swap was made
                swapped = True

    if form.validate_on_submit():
        # Splits the comment message into its individual words
        split_comment = form.content.data.split()
        # Retrieves the list of banned words from the banned word table
        banned_word = []
        for word in BannedWord.query.all():
            banned_word.append(word.word)
        # Iterates through each word in the submitted comment
        for word in split_comment:
            for bannedword in banned_word:
                # If the word matches a banned word that it is replaced with hashtag symbol
                if word == bannedword:
                    form.content.data = form.content.data.replace(word, "#" * len(word))
        comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post_id)
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been posted', 'success')
        return redirect(url_for('post', post_id=post_id))
    return render_template('post.html', post=post, form=form, comments=comments)

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
    # Queries the database for a post object with the given post_id
    # Raises a 404 error if the post with that ID is not found
    post = Post.query.get_or_404(post_id)
    # Will raises a forbidden access error if the user is not the owner of the post or a moderator
    if post.user != current_user and current_user.role != 'moderator':
        abort(403)

    # Deletes the associated comments before deleting the post
    comments = Comment.query.filter_by(post_id=post_id).all()
    for comment in comments:
        db.session.delete(comment)

    # If user has the required permissions, deletes post object and commits changes to the database
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted', 'success')
    return redirect(url_for('home'))

def moderator_required(route_function):
    # Preserves the meta data of the original route function
    @wraps(route_function)
    # Defines function that accepts any number of positional and keyword arguments
    def decorated_function(*args, **kwargs):
        # Checks if the current user is authenticated and has a role of moderator
        if current_user.is_authenticated and current_user.role == 'moderator':
            # Calls the original route function with the given arguments
            return route_function(*args, **kwargs)
        else:
            # Will display an error message and redirect to the home page
            flash('You must be logged in as a moderator to access this page', 'danger')
            return redirect(url_for('home'))
    return decorated_function

@app.route("/banned_words", methods=['GET', 'POST'])
@login_required
@moderator_required
def banned_words():
    # Creates an instance of the banned word form
    form = BannedWordForm()

    # Checks if form has been submitted and data is valid
    if form.validate_on_submit():
        # Creates banned word object with data passed into the form
        new_banned_word = BannedWord(word=form.word.data)
        # Adds banned word to the database and commits the changes
        db.session.add(new_banned_word)
        db.session.commit()
        flash('Banned word has been added', 'success')
        return redirect(url_for('banned_words'))
    elif request.method == 'GET':
        banned_word = BannedWord.query.all()
    return render_template('banned_words.html', form=form, banned_word=banned_word)

@app.route("/banned_word/<int:id>/delete", methods=['GET', 'POST'])
@login_required
@moderator_required
def delete_banned_word(id):
    # Queries the database for a banned word object with the given ID
    # Raises a 404 error if the banned word with that ID is not found
    word_to_delete = BannedWord.query.get_or_404(id)
    # Will raises a forbidden access error if the user is not a moderator
    if current_user.role != 'moderator':
        abort(403)

    # If user has the required permissions, deletes banned word and commits changes to the database
    db.session.delete(word_to_delete)
    db.session.commit()
    flash('Banned word has been deleted', 'success')
    return redirect(url_for('banned_words'))

@app.route("/post/<int:post_id>/like", methods=['GET', 'POST'])
@login_required
def like_post(post_id):
    # Retrieves the post with the given post_id from the database
    post = Post.query.get_or_404(post_id)
    # Queries the like table to see if the current user has already liked the post
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if like:
        # Deletes the like from the database if a like exists
        db.session.delete(like)
        db.session.commit()
        flash('You unliked the post', 'success')
    else:
        # If a like does not exist, then a new like object is created and added to the database
        new_like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(new_like)
        db.session.commit()
        flash('You liked the post', 'success')
    return redirect(url_for('home'))