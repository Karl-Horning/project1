import os

from flask import Flask, render_template, session
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from books.forms import LoginForm
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@app.route("/index")
def index():
    user = {'username': 'Karl'}
    # return "Project 1: TODO"
    return render_template('index.html', user=user)

@app.route("/login")
def login():
    form = LoginForm()
    return render_template('login.html', form=form)
