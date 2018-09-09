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
    books = Book.query.limit(25).all()
    return render_template('index.html', books=books)

# @app.route('/books/<book_isbn>')
# def books(book_isbn):
#     """List the details of a book"""
#     book = Book.query.with_entities(Book.isbn)
#     # book = Book.query.get(book_id)
#     if book is None:
#         return render_template('error.html', message=f'No book with the ISBN {book_isbn} exists.')

#     return render_template('book.html', book=book)

@app.route('/books/<int:book_id>')
def books(book_id):
    """List the details of a book"""
    book = Book.query.get(book_id)
    if book is None:
        return render_template('error.html', message=f'No book with the ID {book_id} exists.')

    # Make request to Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": Config.KEY, "isbns": book.isbn})
    # Create an object with the needed JSON data
    class Goodreads(object):
        average_rating = res.json()['books'][0]['average_rating']
        number_of_ratings = locale.format('%d', res.json()['books'][0]['work_ratings_count'], grouping=True)

    return render_template('book.html', book=book, Goodreads=Goodreads)