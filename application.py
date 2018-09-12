from flask import Flask, render_template, jsonify, request
from models import *
from config import Config

import locale
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
locale.setlocale(locale.LC_ALL, 'en_GB')

@app.route('/')
def index():
    books = db.engine.execute('SELECT * FROM books LIMIT 50')
    return render_template('index.html', books=books)

@app.route('/books/<isbn>')
def books(isbn):
    """List the details of a book"""
    book =  db.engine.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'").fetchone()
    if book is None:
        return render_template('error.html', message=f'No book with the ID {isbn} exists.')

    # Make request to Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": Config.KEY, "isbns": isbn})
    # Create an object with the needed JSON data
    class Goodreads(object):
        average_rating = res.json()['books'][0]['average_rating']
        number_of_ratings = locale.format('%d', res.json()['books'][0]['work_ratings_count'], grouping=True)

    return render_template('book.html', book=book, Goodreads=Goodreads)

@app.route('/api/<isbn>')
def api(isbn):
    """List the book's API"""
    book =  db.engine.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'").fetchone()
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": Config.KEY, "isbns": isbn})

@app.route('/test')
def test():
    q = 'dav'
    # books = db.engine.execute("SELECT * FROM books WHERE LOWER(author) = LOWER('Henry James')")
    # books = db.engine.execute(f"SELECT * FROM books WHERE LOWER(author) LIKE LOWER('%%{q}%%')")
    books = db.engine.execute(f"SELECT * FROM books WHERE isbn = '0316010766'")
    return render_template('test.html', books=books)