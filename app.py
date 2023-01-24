from flask import Flask, render_template, request

# this will convert the file into a web application
app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")
