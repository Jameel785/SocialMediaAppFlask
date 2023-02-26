from flask import Flask, render_template, request, url_for

# this will convert the file into a web application
app = Flask(__name__)

# users can access the home page using the home path or default path
@app.route("/home")
@app.route("/")
def home():
    return render_template("home.html", title="home")

# Access the login page with the login route
@app.route("/login")
def login():
    return render_template("login.html", title="login")

# Access the register page with the register route
@app.route("/register")
def register():
    return render_template("register.html", title="register")
