from flask import Flask, render_template, jsonify, request
from models import *
from config import Config

import locale
import os
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

@app.route('/book/<isbn>')
def book(isbn):
    """List the details of a book"""
    book =  db.engine.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'").fetchone()

    if book is None:
        return render_template('404.html'), 404

    # Make request to Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": Config.KEY, "isbns": isbn})
    # Create an object with the needed JSON data
    class Goodreads(object):
        average_rating = res.json()['books'][0]['average_rating']
        number_of_ratings = locale.format('%d', res.json()['books'][0]['work_ratings_count'], grouping=True)

    return render_template('book.html', book=book, Goodreads=Goodreads)

@app.route('/api/<isbn>')
def book_api(isbn):
    """List the details of a book as JSON"""
    book =  db.engine.execute(f"SELECT * FROM books WHERE isbn = '{isbn}'").fetchone()
    
    if book is None:
        return render_template('404.html'), 404
    
    # Make request to Goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": Config.KEY, "isbns": isbn})
    # Create an object with the needed JSON data
    class Goodreads(object):
        average_rating = res.json()['books'][0]['average_rating']
        number_of_ratings = res.json()['books'][0]['work_ratings_count']
    return jsonify({
        "title": book[2],
        "author": book[3],
        "year": book[4],
        "isbn": book[1],
        "review_count": Goodreads.number_of_ratings,
        "average_score": Goodreads.average_rating
    })

@app.route('/test', methods=['POST', 'GET'])
def test():
    if request.method == 'POST':
        q = request.form['q']
    else:
        q = '0316010766'
    # books = db.engine.execute("SELECT * FROM books WHERE LOWER(author) = LOWER('Henry James')")
    # books = db.engine.execute(f"SELECT * FROM books WHERE LOWER(author) LIKE LOWER('%%{q}%%')")
    
    # books = db.engine.execute(f"SELECT * FROM books \
    #                             WHERE isbn = '{q}'")

    books = db.engine.execute(f"SELECT * FROM books \
                                WHERE ( \
                                    isbn LIKE '{q}' \
                                ) \
                                OR ( \
                                    LOWER(title) LIKE LOWER('%%{q}%%') \
                                ) \
                                OR ( \
                                    LOWER(author) LIKE LOWER('%%{q}%%') \
                                ) \
                                ORDER BY ( \
                                    ( \
                                        CASE WHEN author LIKE LOWER('%%{q}%%') \
                                        THEN 1 \
                                        ELSE 0 \
                                        END \
                                    ) \
                                    + ( \
                                        CASE WHEN isbn LIKE LOWER('{q}') \
                                        THEN 1 \
                                        ELSE 0 \
                                        END \
                                    ) \
                                    + ( \
                                        CASE WHEN title LIKE LOWER('%%{q}%%') \
                                        THEN 1 \
                                        ELSE 0 \
                                        END \
                                    ) \
                                ) \
                                DESC")
    return render_template('test.html', books=books)

@app.route('/register')
def register():
    """Register a new user"""
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    return render_template('register.html')


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404