from pymongo import MongoClient

from app.constants.mongodb_constants import MongoCollections
from app.models.book import Book
from app.utils.logger_utils import get_logger
from config import MongoDBConfig

logger = get_logger('MongoDB')


class MongoDB:
    def __init__(self, connection_url=None):
        if connection_url is None:
            connection_url = f'mongodb://{MongoDBConfig.USERNAME}:{MongoDBConfig.PASSWORD}@{MongoDBConfig.HOST}:{MongoDBConfig.PORT}'

        self.connection_url = connection_url.split('@')[-1]
        self.client = MongoClient(connection_url)
        self.db = self.client[MongoDBConfig.DATABASE]

        self._books_col = self.db[MongoCollections.books]

    def get_books(self, filter_=None, projection=None):
        try:
            if not filter_:
                filter_ = {}
            cursor = self._books_col.find(filter_, projection=projection)
            data = []
            for doc in cursor:
                data.append(Book().from_dict(doc))
            return data
        except Exception as ex:
            logger.exception(ex)
        return []

    # def add_book(self, book: Book):
    #     try:
    #         inserted_doc = self._books_col.insert_one(book.to_dict())
    #         return inserted_doc
    #     except Exception as ex:
    #         logger.exception(ex)
    #     return None

    # TODO: write functions CRUD with books
    def add_book(self, book: Book):
        try:
            doc = self._books_col.insert_one(book.to_dict())
            return doc
        except Exception as ex:
            return None

    def del_book(self, book: Book):
        try:
            del_doc = self._books_col.delete_one(book.to_dict())
            print(del_doc.deleted_count, " books deleted")
            return True
        except Exception as ex:
            return None

    def update_book(self, book_id, update={}):
        try:

            updated_doc = self._books_col.update_one({"_id":book_id},{"$set":update})
            return updated_doc
        except Exception as ex:
            return None
