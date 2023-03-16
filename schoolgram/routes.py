from flask import render_template, request, url_for, flash, redirect
from schoolgram import app, db, bcrypt
from schoolgram.forms import RegistrationForm, LoginForm
from schoolgram.models import User, Post, Comment, Like
from flask_login import login_user

# users can access the home page using the home path or default path
@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html", title="home")

# Access the login page with the login route
@app.route("/login", methods=['GET', 'POST'])
def login():
    # Creates an instance of the login form
    form = LoginForm()

    # If the form has been submitted and is valid,
    # Flash a login success message and redirect the user to the home page
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')

    # Render the login template with the form instance
    return render_template("login.html", title="login", form=form)

# Access the register page with the register route
@app.route("/register", methods=['GET', 'POST'])
def register():
    # Creates an instance of the registration form
    form = RegistrationForm()

    # If the form has been submitted and is valid,
    # Flash an account created success message and redirect the user to the home page
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        flash('Account has been created', 'success')
        return redirect(url_for('login'))

    # Render the register template with the form instance
    return render_template("register.html", title="register", form=form)