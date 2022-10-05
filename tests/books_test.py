from main import app
import json
import unittest
from tests import test_constants
from app.databases.mongodb import MongoDB
_db = MongoDB()
class BooksTests(unittest.TestCase):
    """ Unit testcases for REST APIs """

    def test_get_all_books(self):
        request, response = app.test_client.get('/books')
        self.assertEqual(response.status, 200)
        data = json.loads(response.text)
        self.assertGreaterEqual(data.get('n_books'), 0)
        self.assertIsInstance(data.get('books'), list)

    # TODO: unittest for another apis
    def test_read_book(self):
        book_id = test_constants.book_id
        request,response = app.test_client.get(f'/books/{book_id}')
        self.assertEqual(response.status,200)
        data = json.loads(response.text)
        self.assertIsInstance(data.get('title'), str)
        self.assertIsInstance(data.get('authors'), list)
        self.assertIsInstance(data.get('publisher'), str)

    def test_post_book_no_login(self):
        body = test_constants.PostBook
        headers = {'Authorization': ''}
        request, response = app.test_client.post('/books', headers=headers, data=body)
        self.assertEqual(response.status, 401)
        self.assertEqual(json.loads(response.text).get('message'), "Unauthorized: You are unauthorized.")

    # def test_post_book_login(self):
    #     body = test_constants.PostBook
    #     })
    #     user = test_constants.user
    #     })
    #     user = _db.get_user({})
    #     request_user, response_user = app.test_client.post('/books/login', data=user)
    #     data = json.loads(response_user.text)
    #     token = data.get('token')
    #     headers = {'Authorization': token}
    #     request, response = app.test_client.post('/books', headers=headers, data=body)
    #     self.assertEqual(response.status, 200)

    def test_get_book_by_wrong_id(self):
        book_id = 0
        request, response = app.test_client.get(f'/books/{book_id}')
        self.assertEqual(response.status, 404)
        # self.assertEqual(json.loads(response.text).get('message'), "Not Found: ")

    # def test_put_book_no_login(self):
    #     # book = _db.get_book()
    #     # book_id = book.get("_id")
    #     # body = json.dumps({
    #     #     "title": "Test"
    #     # })
    #     # headers = {'Authorization': ''}
    #     # request, response = app.test_client.put('/books/{}'.format(book_id), headers=headers, data=body)
    #     # self.assertEqual(response.status, 401)
    #     # self.assertEqual(json.loads(response.text).get('message'), "Unauthorized: You are unauthorized.")

    def test_put_book_wrong_id(self):
        user = test_constants.user
        body = json.dumps({
            "title": "Test"
        })
        book_id = 0

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.put('/books/{}'.format(book_id), headers=headers, data=body)
        self.assertEqual(response.status, 404)
        # self.assertEqual(json.loads(response.text).get('message'), "Not Found: ")

    def test_put_book_id(self):
        user = test_constants.PostBook
        body = json.dumps({
            "title": "Test"
        })
        book = _db.get_book({})
        book_id = book.get("_id")

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.put('/books/{}'.format(book_id), headers=headers, data=body)
        self.assertEqual(response.status, 200)
        data_response = json.loads(response.text)
        self.assertIsInstance(data_response.get('book'), object)

    # need check the owner
    def test_put_book_id_no_owner(self):
        user = test_constants.user
        body = json.dumps({
            "title": "Test"
        })

        book_id = test_constants.book_id

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.put('/books/{}'.format(book_id), headers=headers, data=body)
        self.assertEqual(response.status, 403)
        self.assertEqual(json.loads(response.text).get('message'), "Forbidden: You are not owner of book")

    # need check the owner
    def test_put_book_id_owner(self):
        user = test_constants.user
        body = json.dumps({
            "title": "Test"
        })

        book_id = test_constants.book_id

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.put('/books/{}'.format(book_id), headers=headers, data=body)
        self.assertEqual(response.status, 200)
        data_response = json.loads(response.text)
        self.assertIsInstance(data_response.get('book'), object)

    def test_delete_book_no_login(self):
        book = _db.get_book({})
        book_id = book.get("_id")
        headers = {'Authorization': ''}
        request, response = app.test_client.delete('/books/{}'.format(book_id), headers=headers)
        self.assertEqual(response.status, 401)
        # self.assertEqual(json.loads(response.text).get('message'), "Unauthorized: You are unauthorized.")

    def test_delete_book_wrong_id(self):
        user = test_constants.user

        book_id = 0

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.delete('/books/{}'.format(book_id), headers=headers)
        self.assertEqual(response.status, 404)
        # self.assertEqual(json.loads(response.text).get('message'), "Not Found: ")

    # need check the owner
    def test_delete_book_id_no_owner(self):
        user = test_constants.user


        book_id = test_constants.book_id

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.delete('/books/{}'.format(book_id), headers=headers)
        self.assertEqual(response.status, 403)
        # self.assertEqual(json.loads(response.text).get('message'), "Forbidden: You are not owner of book")


    def test_delete_book_id_owner(self):
        user = test_constants.user
        # GET id of book
        # book = _db.get_book({})
        # book_id = book.get("_id")
        book_id = test_constants.book_id

        request_user, response_user = app.test_client.post('/books/login', data=user)
        data = json.loads(response_user.text)
        token = data.get('token')
        headers = {'Authorization': token}
        request, response = app.test_client.delete('/books/{}'.format(book_id), headers=headers)
        self.assertEqual(response.status, 200)
        data_response = json.loads(response.text)
        self.assertIsInstance(data_response.get('book'), object)


if __name__ == '__main__':
    unittest.main()
