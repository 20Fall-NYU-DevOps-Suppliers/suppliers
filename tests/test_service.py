"""
Supplier API Service Test Suite
Test cases can be run with the following:
nosetests -v --with-spec --spec-color
nosetests --stop tests/test_service.py:TestSupplierServer
"""

import unittest
import logging
from flask_api import status
from werkzeug.datastructures import MultiDict, ImmutableMultiDict
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
    """ Test Cases for Supplier Service """


    def setUp(self):
        self.app = service.app.test_client()
        service.initialize_logging(logging.INFO)
        service.init_db("test")
        service.data_reset()


    def _create_suppliers(self, count):
        """ Factory method to create suppliers in bulk """
        suppliers = []
        for _ in range(count):
            test_supplier = SupplierFactory()
            resp = self.app.post(
                "/suppliers", json=test_supplier.serialize(), content_type="application/json"
            )
            self.assertEqual(
                resp.status_code, status.HTTP_201_CREATED, "Could not create test suppliers"
            )
            new_supplier = resp.get_json()
            test_supplier.id = new_supplier["_id"]
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


    def test_query_by_name(self):
        """ Query Suppliers by name """
        suppliers = self._create_suppliers(5)
        test_name = suppliers[0].name
        name_suppliers = [supplier for supplier in suppliers if supplier.name == test_name]
        resp = self.app.get("/suppliers", query_string="name={}".format(test_name))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(name_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier['name'], test_name)


    def test_query_by_like_count(self):
        """ Query Suppliers with like count limit"""
        suppliers = self._create_suppliers(5)
        like_limit = suppliers[0].like_count
        like_count_suppliers = [supplier for supplier in suppliers
                                if supplier.like_count > like_limit]
        resp = self.app.get("/suppliers", query_string="like_count={}".format(like_limit))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(like_count_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertGreater(supplier['like_count'], like_limit)


    def test_query_by_is_active(self):
        """ Query Suppliers by is_active """
        suppliers = self._create_suppliers(5)
        test_is_active = suppliers[0].is_active
        test_is_active_str = 'true' if test_is_active else 'false'
        is_active_suppliers = [supplier for supplier in suppliers
                               if supplier.is_active == test_is_active]
        resp = self.app.get("/suppliers", query_string="is_active={}".format(test_is_active_str))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(is_active_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertEqual(supplier['is_active'], test_is_active)


    def test_query_by_rating(self):
        """ Query Suppliers with rating limit """
        suppliers = self._create_suppliers(5)
        rating_limit = suppliers[0].rating
        rating_suppliers = [supplier for supplier in suppliers if supplier.rating > rating_limit]
        resp = self.app.get("/suppliers", query_string="rating={}".format(rating_limit))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(rating_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertGreater(supplier['rating'], rating_limit)


    def test_query_by_product_id(self):
        """ Query Suppliers by product id """
        suppliers = self._create_suppliers(5)
        test_product_id = suppliers[0].products[0]
        all_suppliers = [supplier for supplier in suppliers if test_product_id in supplier.products]
        resp = self.app.get("/suppliers", query_string="product_id={}".format(test_product_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(all_suppliers))
        # check the data just to be sure
        for supplier in data:
            self.assertIn(test_product_id, supplier['products'])


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
        supplier_count = self.get_supplier_count()
        new_supplier = SupplierFactory()
        resp = self.app.post('/suppliers', json=new_supplier.serialize(),
                             content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        location = resp.headers.get('Location')
        self.assertNotEqual(location, None)
        new_json = resp.get_json()
        self.assertEqual(new_json['name'], new_supplier.name)
        self.assertEqual(new_json['like_count'], new_supplier.like_count)
        self.assertEqual(new_json['products'], new_supplier.products)
        self.assertEqual(new_json['rating'], new_supplier.rating)
        self.assertEqual(new_json['is_active'], new_supplier.is_active)
        # check that count has gone up and includes sammy
        resp = self.app.get('/suppliers')
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertEqual(resp.status_code, HTTP_200_OK)
        self.assertEqual(len(data), supplier_count + 1)


    def test_create_supplier_from_formdata(self):
        supplier_data = MultiDict()
        supplier_data.add('name', 'supplier1')
        supplier_data.add('like_count', 2)
        supplier_data.add('products', [1, 2, 3])
        supplier_data.add('rating', 8.5)
        supplier_data.add('is_active', True)
        data = ImmutableMultiDict(supplier_data)
        resp = self.app.post('/suppliers', data=data,
                             content_type='application/x-www-form-urlencoded')
        self.assertEqual(resp.status_code, HTTP_201_CREATED)
        # Make sure location header is set
        location = resp.headers.get('Location', None)
        self.assertNotEqual(location, None)
        # Check the data is correct
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertEqual(data['name'], 'supplier1')


    def test_create_supplier_with_no_name(self):
        """ Create a Supplier without a name """
        new_supplier = SupplierFactory()
        new_supplier.name = None
        resp = self.app.post('/suppliers', json=new_supplier.serialize(),
                             content_type='application/json')
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


    def test_like_supplier(self):
        """ Like a Supplier """
        test_supplier = SupplierFactory()
        posted_resp = self.app.post('/suppliers', json=test_supplier.serialize(),
                                    content_type='application/json')
        posted_data = posted_resp.get_json()
        resp = self.app.put("/suppliers/{}/like".format(posted_data['_id'],
                                                        content_type="application/json"))
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['like_count'], test_supplier.like_count+1)


    def test_like_supplier_non_found(self):
        """ Like a Supplier that doesn't exist """
        resp = self.app.put('/suppliers/0/like')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)
        data = resp.get_json()
        logging.debug('data = %s', data)
        self.assertIn('was not found', data['message'])


    def test_like_supplier_wrong_method(self):
        """ Like a Supplier using wrong HTTP method """
        test_supplier = SupplierFactory()
        posted_resp = self.app.post('/suppliers', json=test_supplier.serialize(),
                                    content_type='application/json')
        posted_data = posted_resp.get_json()
        resp = self.app.post("/suppliers/{}/like".format(posted_data['_id'],
                                                        content_type="application/json"))
        self.assertEqual(resp.status_code, HTTP_405_METHOD_NOT_ALLOWED)


    def test_update_supplier(self):
        """ Update a Supplier """
        test_supplier = self._create_suppliers(1)[0]
        test_supplier.name = "test_update"
        resp = self.app.put('/suppliers/{}'.format(test_supplier.id),
                            json=test_supplier.serialize(), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        resp = self.app.get('/suppliers/{}'.format(test_supplier.id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['name'], 'test_update')


    def test_update_supplier_with_no_name(self):
        """ Update a Supplier without assigning a name """
        test_supplier = self._create_suppliers(1)[0]
        test_supplier.name = None
        resp = self.app.put('/suppliers/{}'.format(test_supplier.id),
                            json=test_supplier.serialize(), content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_400_BAD_REQUEST)


    def test_update_supplier_not_found(self):
        """Update a Supplier that does not exist"""
        new_supplier = SupplierFactory()
        resp = self.app.put('/suppliers/0', json=new_supplier.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_404_NOT_FOUND)


    def test_delete_supplier(self):
        """ Delete a Supplier """
        test_suppliers = self._create_suppliers(5)
        self.assertEqual(len(test_suppliers), 5)

       # delete a supplier
        resp = self.app.delete('/suppliers/{}'.format(test_suppliers[0].id),
                               content_type='application/json')
        self.assertEqual(resp.status_code, HTTP_204_NO_CONTENT)
        self.assertEqual(len(resp.data), 0)
        new_count = self.get_supplier_count()
        self.assertEqual(new_count, len(test_suppliers)-1)


######################################################################
# Utility functions
######################################################################
    def get_supplier_count(self):
        """ save the current number of suppliers """
        resp = self.app.get('/suppliers')
        self.assertEqual(resp.status_code, HTTP_200_OK)
        data = resp.get_json()
        logging.debug('data = %s', data)
        return len(data)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestService)
    unittest.TextTestRunner(verbosity=2).run(suite)
