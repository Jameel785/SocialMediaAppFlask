from flask import render_template, request, url_for, flash, redirect
from schoolgram import app, db, bcrypt
from schoolgram.forms import RegistrationForm, LoginForm
from schoolgram.models import User, Post, Comment, Like
from flask_login import login_user, current_user, logout_user, login_required

# users can access the home page using the home path or default path
@app.route("/home")
@login_required
def home():
    return render_template("home.html", title="home")

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
            # Redirect to the home page after a successful login
            return redirect(url_for('home'))
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

@app.route("/account")
@login_required
def account():
    return render_template("account.html", title="Account")