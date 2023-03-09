from datetime import datetime
from flask import Flask, render_template, request, url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from forms import RegistrationForm, LoginForm


# this will convert the file into a web application
app = Flask(__name__)

app.config['SECRET_KEY'] = '15fe26a73acd9ed948d11ca07f2b50aa'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)

    def __repr__(self):
        return f"User('{self.username}', {self.email}', {self.role}', {self.image_file}')"

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    caption = db.Column(db.String(200))
    image_file = db.Column(db.String(20))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    likes = db.relationship('Like', backref='post', lazy=True)
    comments = db.relationship('Comment', backref='post', lazy=True)

    def __repr__(self):
        return f"Post('{self.caption}', {self.date_posted}')"

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.content}', '{self.date_posted}')"

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

    def __repr__(self):
        return f"Comment('{self.user_id}', '{self.post_id}')"

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
        if form.email.data == 'student1@lydiardparkacademy.org.uk' and form.password.data == 'password':
            flash('You have been logged in', 'success')
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')

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
        flash(f'Account created for {form.username.data}', 'success')
        return redirect(url_for('home'))

    # Render the register template with the form instance
    return render_template("register.html", title="register", form=form)
