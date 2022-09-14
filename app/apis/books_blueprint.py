import uuid

from sanic import Blueprint
from sanic.response import json
from sanic_openapi.openapi2 import doc
# from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
# from app.databases.redis_cached import get_cache, set_cache
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError
from app.models.book import create_book_json_schema, Book, PostBook,PostUpdateBook

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()


@books_bp.route('/books')
async def get_all_books(request):
    # # TODO: use cache to optimize api
    # async with request.app.ctx.redis as r:
    #     books = await get_cache(r, CacheConstants.all_books)
    #     if books is None:
    #         book_objs = _db.get_books()
    #         books = [book.to_dict() for book in book_objs]
    #         await set_cache(r, CacheConstants.all_books, books)

    book_objs = _db.get_books()
    books = [book.to_dict() for book in book_objs]
    number_of_books = len(books)
    return json({
        'n_books': number_of_books,
        'books': books
    })


@books_bp.route('/books/<book_id>/create', methods={'POST'})
# @protected  # TODO: Authenticate
@doc.consumes(doc.String(name='book_id',required=True),location='path',required=True)
@doc.consumes(PostBook,location='body',required=True)
@validate_with_jsonschema(create_book_json_schema)  # To validate request body
async def create_book(request, username=None):
    body = request.json

    book_id = str(uuid.uuid4())
    book = Book(book_id).from_dict(body)
    book.owner = username

    # # TODO: Save book to database
    inserted = _db.add_book(book)
    if not inserted:
        raise ApiInternalError('Fail to create book')

    # TODO: Update cache

    return json({'status': 'success'})


# TODO: write api get, update, delete book

@books_bp.route('/', methods={'PUT'})
# @protected  #TODO: Authenticate
@doc.consumes(doc.String(name='book_id',required=True),location='path',required=True)
@doc.consumes(PostUpdateBook,location='body',required=True)
async def update_book(request):
    body = request.json
    book_id = body["book_id"]
    update = body["update"]
    updated = _db.update_book(book_id=book_id,update=update)
    if not updated:
        raise ApiInternalError('Fail to update book')
    return json({'status':'success'})


@books_bp.route('/books/<book_id>/delete', methods={'Delete'})
# @protected  #TODO: Authenticate
@doc.consumes(doc.String(name='book_id',required=True),location='path',required=True)
async def del_book(request,book_id,update={}):
    deleted = _db.del_book(book_id,update)
    if not deleted:
        raise ApiInternalError('Fail to delete book')
    return json({'status':'success'})







