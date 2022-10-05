import uuid
from sanic import Blueprint
from sanic.response import json
from sanic_openapi.openapi2 import doc

from app.decorators.auth import protected
from app.utils import jwt_utils
from app.constants.cache_constants import CacheConstants
from app.databases.mongodb import MongoDB
from app.databases.redis_cached import get_cache, set_cache
from app.decorators.json_validator import validate_with_jsonschema
from app.hooks.error import ApiInternalError, ApiNotFound, ApiForbidden, ApiBadRequest
from app.models.book import create_book_json_schema, Book, PostBook, PostUpdateBook, PostLogin,update_book_json_schema,login_json_schema

books_bp = Blueprint('books_blueprint', url_prefix='/books')

_db = MongoDB()


@books_bp.route('/', methods={"GET"})
@doc.summary('Get all books')
async def get_all_books(request):
    # TODO: use cache to optimize api
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            await set_cache(r, CacheConstants.all_books, books)

    book_objs = _db.get_books()
    books = [book.to_dict() for book in book_objs]
    number_of_books = len(books)
    return json({
        'n_books': number_of_books,

        'books': books
    })


@books_bp.route('/', methods={'POST'})
@protected
@doc.consumes(PostBook, location='body', required=True)
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
    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        if books is None:
            book_objs = _db.get_books()
            books = [book.to_dict() for book in book_objs]
            await set_cache(r, CacheConstants.all_books, books)
        books.append(book.to_dict())
        await set_cache(r, CacheConstants.all_books, books)

    return json({'status': 'success'}, status=201)


# TODO: write api get, update, delete book

@books_bp.route('<book_id>/', methods={'GET'})
@doc.consumes(doc.String(name="book_id", description="book_id"), location="path", required=True)
async def read_book(request, book_id):
    book_obj = _db.get_books(filter_={"_id": book_id})
    if not book_obj:
        raise ApiNotFound(f'book detail not found with id {book_id}')
    book = [book.to_dict() for book in book_obj]

    return json(book[0])


@books_bp.route('<book_id>/', methods={'PUT'})
@protected
@doc.consumes(PostUpdateBook, location='body', required=True)
@doc.consumes(doc.String(name="book_id", description="book_id"), location="path", required=True)
@validate_with_jsonschema(update_book_json_schema)
async def update_book(request, book_id, username=None):
    body = request.json
    book = _db.get_books(filter_={"_id": book_id})

    if not book:
        raise ApiNotFound(f'can not find book with id {book_id} to update')
    book_dict = book[0].to_dict()
    if book_dict['owner'] != username:
        raise ApiForbidden('you are not the owner of this book')


    updated = _db.update_book(book_id=book_id, update=body)

    if not updated:
        raise ApiInternalError('Fail to update book')

    async with request.app.ctx.redis as r:
        books = await get_cache(r, CacheConstants.all_books)
        books.remove(book)
        books.append(updated)
        await set_cache(r, CacheConstants.all_books, books)
    return json({'status': 'success'})


@books_bp.route('<book_id>/', methods={'Delete'})
@doc.consumes(doc.String(name="book_id", description="book_id"), location="path", required=True)
@protected
async def del_book(request, book_id, username=None):
    book = _db.get_books(filter_={"_id": book_id})
    if not book:
        raise ApiNotFound(f'can not find book with id {book_id} to delete')
    book_dict = book[0].to_dict()
    if book_dict['owner'] != username:
        raise ApiForbidden('you are not the owner of this book')
    deleted = _db.del_book(book_id)

    if not deleted:
        raise ApiInternalError('Fail to delete book')
    # async with request.app.ctx.redis as r:
    #     books = await get_cache(r, CacheConstants.all_books)
    #
    #     books.remove(deleted)
    #     await set_cache(r, CacheConstants.all_books, books)
    return json({'status': 'success'})


@books_bp.route('/register', methods={'POST'})
@doc.consumes(PostLogin, location='body', required=True)
@validate_with_jsonschema(login_json_schema)
async def register(request):
    body = request.json
    username = body['username']
    password = body['password']
    if _db.get_user(filter_={'username': username}):
        raise ApiBadRequest("username already existed")
    else:
        _db.add_user(body)

        return json({'status': 'successful'})


@books_bp.route('/login', methods={'POST'})
@doc.consumes(PostLogin, location='body', required=True)
@validate_with_jsonschema(login_json_schema)
async def login(request):
    body = request.json
    username = body['username']
    password = body['password']
    user = _db.get_user(filter_={'username': username})
    if not user:
        raise ApiBadRequest("username does not exist")
    if user[0]["password"] != password :
        raise ApiBadRequest("password not corrected")
    _jwt = jwt_utils.generate_jwt(username)

    return json({'status': 'successful',
                 'jwt': _jwt})
