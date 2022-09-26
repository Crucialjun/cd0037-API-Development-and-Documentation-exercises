import os

from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy  # , or_
from flask_cors import CORS
import random

from models import setup_db, Book


BOOKS_PER_SHELF = 15

# @TODO: General Instructions
#   - As you're creating endpoints, define them and then search for 'TODO' within the frontend to update the endpoints there.
#     If you do not update the endpoints, the lab will not work - of no fault of your API code!
#   - Make sure for each route that you're thinking through when to abort and with which kind of error
#   - If you change any of the response body keys, make sure you update the frontend to correspond.


def paginate(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * BOOKS_PER_SHELF
    end = start + BOOKS_PER_SHELF
    formatted_books = [book.format() for book in selection]
    return formatted_books[start:end]


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    # CORS Headers
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    @app.route("/books")
    def get_books():

        books = Book.query.all()

        formatted_books = paginate(request, books)

        if (len(formatted_books) == 0):
            abort(404)

        return jsonify({
            "success": True,
            "books": formatted_books,
            'total_books': len(formatted_books)
        })

    @app.route("/books/<int:book_id>", methods=['PATCH'])
    def update_book(book_id):
        body = request.get_json

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()
            if book is None:
                abort(404)
            if 'rating' in body:
                book.rating = int(body.get('rating'))

            book.update()

            return jsonify({
                "success": True,
                "id": book.id
            })

        except:
            abort(404)

    @app.route("/books/<int:book_id>", methods=['DELETE'])
    def delete_book(book_id):
        body = request.get_json

        try:
            book = Book.query.filter(Book.id == book_id).one_or_none()

            if book is None:
                abort(404)

            book.delete()
            selection = Book.query.order_by(Book.id).all()
            current_books = paginate(request, selection)

            return jsonify({
                "success": True,
                "deleted": book_id,
                'books': current_books,
                'total_books': len(Book.query.all())
            })

        except:
            abort(422)

    @app.route("/books", methods=['POST'])
    def create_book(book_id):
        body = request.get_json

        new_title = body.get('title', None)
        new_author = body.get('author', None)
        new_rating = body.get('rating', None)

        try:
            book = Book(title=new_title, author=new_author, rating=new_rating)
            book.insert()

            selection = Book.query.order_by(Book.id).all()
            current_books = paginate(request, selection)

            return jsonify({
                "success": True,
                "created": book_id,
                'books': current_books,
                'total_books': len(Book.query.all())
            })

        except:
            abort(422)

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            'error': 404,
            'message': "Resource Not Found"
        }), 404

    @app.errorhandler(422)
    def unproccesable(error):
        return jsonify({
            "success": False,
            'error': 422,
            'message': "Resource Unproccesable"
        }), 404

    return app
