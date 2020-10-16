"""
Supplier API Service Test Suite
Test cases can be run with the following:
nosetests -v --with-spec --spec-color
nosetests --stop tests/test_service.py:TestSupplierServer
"""

from unittest import TestCase
import logging
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
from service import service

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415

######################################################################
#  T E S T   C A S E S
######################################################################
class TestSupplierServer(TestCase):
    """ Supplier Service tests """

    def setUp(self):
        self.app = service.app.test_client()
        service.initialize_logging(logging.INFO)
        service.init_db("test")
        service.data_reset()
        service.data_load({"name": "supplier1", "like_count": 2, "is_active": True, "products": [1,2,3], "rating": 8.5})
    

    def test_hello(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)
    

    def test_get_supplier_list(self):
        """ Get a list of Suppliers """
        resp = self.app.get('/suppliers')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertIn(len(resp.data) > 0)


    def test_get_supplier(self):
        """ get a single Supplier """
        test_supplier = {"id": 1, "name": "supplier1", "like_count": 2, "is_active": True, "products": [1,2,3], "rating": 8.5}
        post_resp = self.app.post('/suppliers', json=test_supplier, content_type='application/json')
        posted_data = post_resp.get_json()
        resp = self.app.get(
            "/suppliers/{}".format(posted_data['_id']), content_type="application/json"
        )
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], "supplier1")
    
    def test_get_supplier_not_found(self):
        """ Get a Supplier that doesn't exist """
        resp = self.app.get('/suppliers/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertIn('was not found', data['message'])

    def test_create_supplier(self):
        """ Create a new Supplier """
        # save the current number of suppliers for later comparrison
        # supplier_count = self.get_supplier_count()
        # add a new supplier
        new_supplier = {"id": 1, "name": "supplier1", "like_count": 2, "is_active": True, "products": [1,2,3], "rating": 8.5}
        resp = self.app.post('/suppliers', json=new_supplier, content_type='application/json')
        # if resp.status_code == 429: # rate limit exceeded
        #     sleep(1)                # wait for 1 second and try again
        #     resp = self.app.post('/suppliers', data=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        # location = resp.headers.get('Location', None)
        # self.assertNotEqual(location, None)
        # Check the data is correct
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], 'supplier1')
        self.assertEqual(new_json['like_count'], 2)
        self.assertEqual(new_json['products'], [1,2,3])
        self.assertEqual(new_json['rating'], 8.5)
        self.assertEqual(new_json['is_active'], True)
        # check that count has gone up and includes supplier1
        # resp = self.app.get('/suppliers')
        # data = resp.get_json()
        # logging.debug('data = %s', data)
        # self.assertEqual(resp.status_code, HTTP_200_OK)
        # TODO after finishing List Service
        # self.assertEqual(len(data), supplier_count + 1)
        # self.assertIn(new_json, data)
    
    def test_create_supplier_with_no_name(self):
        """ Create a Supplier without a name """
        new_supplier = {'products': [1,2,3], 'is_active': True, 'like_counts': 2, 'rating': 8.5}
        resp = self.app.post('/suppliers', json=new_supplier, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)

    def test_create_supplier_no_content_type(self):
        """ Create a Supplier with no Content-Type """
        resp = self.app.post('/suppliers', data="new_supplier")
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_supplier_wrong_content_type(self):
        """ Create a Supplier with wrong Content-Type """
        data = "wrong_content_type_test_words"
        resp = self.app.post('/suppliers', data=data, content_type='plain/text')
        self.assertEqual(resp.status_code, HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    
    def test_like_supplier_non_found(self):
        """ Like a Supplier that doesn't exist """
        resp = self.app.put('/suppliers/0/like')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertIn('was not found', data['message'])

    def test_like_supplier(self):
        """ Like a Supplier """
        test_supplier = {"id": 1, "name": "supplier1", "like_count": 2, "is_active": True, "products": [1,2,3], "rating": 8.5}
        posted_resp = self.app.post('/suppliers', json=test_supplier, content_type='application/json') 
        posted_data = posted_resp.get_json()
        resp = self.app.put("/suppliers/{}/like".format(posted_data['_id'],content_type="application/json"))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['like_count'], 3)


######################################################################
# Utility functions
######################################################################

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
