"""
Supplier API Service Test Suite
Test cases can be run with the following:
nosetests -v --with-spec --spec-color
nosetests --stop tests/test_service.py:TestSupplierServer
"""

import unittest
import logging
from flask_api import status
from service import service
from .suppliers_factory import SupplierFactory

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
class TestService(unittest.TestCase):
    """ Supplier Service tests """


    def setUp(self):
        self.app = service.app.test_client()
        service.initialize_logging(logging.INFO)
        service.init_db("test")
        service.data_reset()


    def _create_suppliers(self, count):
        """ Factory method to create pets in bulk """
        suppliers = []
        for _ in range(count):
            test_supplier = SupplierFactory()
            resp = self.app.post(
                "/suppliers", json=test_supplier.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test suppliers"
            )
            new_pet = resp.get_json()
            test_supplier.id = new_pet["_id"]
            suppliers.append(test_supplier)
        return suppliers


    def test_hello(self):
        """ Test the index page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, HTTP_200_OK)


    def test_list_suppliers(self):
        """ Get a list of Suppliers """
        self._create_suppliers(10)
        resp = self.app.get('/suppliers')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 10)


    def test_get_supplier(self):
        """ get a single Supplier """
        test_supplier = self._create_suppliers(1)[0]
        resp = self.app.get(
            "/suppliers/{}".format(test_supplier.id), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["name"], test_supplier.name)
        self.assertEqual(data["like_count"], test_supplier.like_count)
        self.assertEqual(data["is_active"], test_supplier.is_active)
        self.assertEqual(data["products"], test_supplier.products)
        self.assertEqual(data["rating"], test_supplier.rating)


    def test_get_supplier_not_found(self):
        """ Get a Supplier that doesn't exist """
        resp = self.app.get('/suppliers/0')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertIn('was not found', data['message'])


    def test_create_supplier(self):
        """ Create a new Supplier """
        new_supplier = SupplierFactory()
        resp = self.app.post('/suppliers', json=new_supplier.serialize(), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], new_supplier.name)
        self.assertEqual(new_json['like_count'], new_supplier.like_count)
        self.assertEqual(new_json['products'], new_supplier.products)
        self.assertEqual(new_json['rating'], new_supplier.rating)
        self.assertEqual(new_json['is_active'], new_supplier.is_active)

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
        new_supplier = SupplierFactory()
        new_supplier.name = None
        resp = self.app.post('/suppliers', json=new_supplier.serialize(), content_type='application/json')
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
        test_supplier = SupplierFactory()
        posted_resp = self.app.post('/suppliers', json=test_supplier.serialize(), content_type='application/json')
        posted_data = posted_resp.get_json()
        resp = self.app.put("/suppliers/{}/like".format(posted_data['_id'], content_type="application/json"))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['like_count'], test_supplier.like_count+1)

    def test_update_supplier(self):
        test_supplier = SupplierFactory()

        post_resp = self.app.post('/suppliers', json=test_supplier.serialize(), content_type='application/json')
        
        posted_data = post_resp.get_json()
        resp = self.app.get("/suppliers/{}".format(posted_data['_id']), content_type="application/json")
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()

        data['name'] = 'supplier2'
 
        resp = self.app.put('/suppliers/{}'.format(data['_id']), json=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        
        resp = self.app.get('/suppliers/{}'.format(data['_id']), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertEqual(data['name'], 'supplier2')
      
    def test_update_supplier_with_no_name(self): 
        new_supplier = SupplierFactory()
        post_resp = self.app.post('/suppliers', json=new_supplier.serialize(), content_type='application/json')
        posted_data = post_resp.get_json()
        
        resp = self.app.get("/suppliers/{}".format(posted_data['_id']), content_type="application/json")
        self.assertEqual(resp.status_code, HTTP_200_OK)

        data = resp.get_json()
        
        del data['name']
        resp = self.app.put('/suppliers/{}'.format(data['_id']), json=data, content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)
      

    def test_update_supplier_not_found(self):
        """Update a Supplier that does not exist"""
        new_supplier = SupplierFactory()
        resp = self.app.put('/suppliers/0', json=new_supplier.serialize(), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)

      

######################################################################
# Utility functions
######################################################################


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestService)
    unittest.TextTestRunner(verbosity=2).run(suite)


