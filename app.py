from flask import Flask, render_template, request, url_for, flash, redirect
from forms import RegistrationForm, LoginForm

# this will convert the file into a web application
app = Flask(__name__)

app.config['SECRET_KEY'] = '15fe26a73acd9ed948d11ca07f2b50aa'

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
