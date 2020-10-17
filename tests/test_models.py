"""
Supplier Test Suite
Test cases can be run with the following:
nosetests -v --with-spec --spec-color
nosetests --stop tests/test_models.py:TestModels
"""

import os
import json
from unittest import TestCase
from unittest.mock import patch
from requests import HTTPError
from service.models import Supplier, DataValidationError, DatabaseConnectionError
from .suppliers_factory import SupplierFactory


VCAP_SERVICES = {
    'cloudantNoSQLDB': [
        {'credentials': {
            'username': 'admin',
            'password': 'pass',
            'host': 'localhost',
            'port': 5984,
            'url': 'http://admin:pass@localhost:5984'
            }
        }
    ]
}

VCAP_NO_SERVICES = {
    'noCloudant': []
}

BINDING_CLOUDANT = {
    'username': 'admin',
    'password': 'pass',
    'host': 'localhost',
    'port': 5984,
    'url': 'http://admin:pass@localhost:5984',
}


######################################################################
#  T E S T   C A S E S
######################################################################
class TestModels(TestCase):
    """ Test Cases for Supplier Model """

    def setUp(self):
        """ Initialize the Cloudant database """
        Supplier.init_db("test")
        Supplier.remove_all()


    @patch('cloudant.client.Cloudant.__init__')
    def test_connection_error(self, bad_mock):
        """ Test Connection error handler """
        bad_mock.side_effect = DatabaseConnectionError()
        self.assertRaises(DatabaseConnectionError, Supplier.init_db, "test")


    def test_create_a_supplier(self):
        """ Create a supplier and assert that it exists """
        supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        supplier.id = 1
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, 1)
        self.assertEqual(supplier.name, "supplier1")
        self.assertEqual(supplier.like_count, 2)
        self.assertEqual(supplier.is_active, True)
        self.assertEqual(supplier.products, [1, 2, 3])
        self.assertEqual(supplier.rating, 8.5)


    def test_add_a_supplier(self):
        """ Create a supplier and add it to the database """
        suppliers = Supplier.all()
        self.assertEqual(suppliers, [])
        supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, None)
        supplier.save()
        # Asert that it was assigned an id and shows up in the database
        self.assertNotEqual(supplier.id, None)
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].name, "supplier1")
        self.assertEqual(suppliers[0].like_count, 2)
        self.assertEqual(suppliers[0].is_active, True)
        self.assertEqual(suppliers[0].products, [1, 2, 3])
        self.assertEqual(suppliers[0].rating, 8.5)


    def test_update_a_supplier(self):
        """ Update a Supplier """
        supplier = SupplierFactory()
        supplier.save()
        self.assertNotEqual(supplier.id, None)
        # Change it an save it
        supplier.rating = 9.0
        supplier.save()
        # Fetch it back and make sure the id hasn't changed
        # but the data did change
        suppliers = Supplier.all()
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].rating, 9.0)
        self.assertEqual(suppliers[0].name, supplier.name)


    def test_delete_a_supplier(self):
        """ Delete a Supplier """
        supplier = SupplierFactory()
        supplier.save()
        self.assertEqual(len(Supplier.all()), 1)
        # delete the supplier and make sure it isn't in the database
        supplier.delete()
        self.assertEqual(len(Supplier.all()), 0)


    def test_serialize_a_supplier(self):
        """ Serialize a Supplier """
        supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        supplier.id = 1
        data = supplier.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('_id', data)
        self.assertEqual(data['_id'], 1)
        self.assertIn('name', data)
        self.assertEqual(data['name'], "supplier1")
        self.assertIn('like_count', data)
        self.assertEqual(data['like_count'], 2)
        self.assertIn('is_active', data)
        self.assertEqual(data['is_active'], True)
        self.assertIn('products', data)
        self.assertEqual(data['products'], [1, 2, 3])
        self.assertIn('rating', data)
        self.assertEqual(data['rating'], 8.5)


    def test_deserialize_a_supplier(self):
        """ Deserialize a Supplier """
        data = {"_id": 1, "name": "supplier1", "like_count": 2, "is_active": True, "products": [1, 2, 3], "rating": 8.5}
        supplier = Supplier()
        supplier.deserialize(data)
        self.assertNotEqual(supplier, None)
        self.assertEqual(supplier.id, 1)
        self.assertEqual(supplier.name, "supplier1")
        self.assertEqual(supplier.like_count, 2)
        self.assertEqual(supplier.is_active, True)
        self.assertEqual(supplier.products, [1, 2, 3])
        self.assertEqual(supplier.rating, 8.5)


    def test_deserialize_with_no_name(self):
        """ Deserialize a Supplier that has no name """
        data = {"like_count": 2, "is_active": True, "products": [1, 2, 3], "rating": 8.5}
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, data)


    def test_deserialize_with_no_data(self):
        """ Deserialize a Supplier that has no data """
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, None)


    def test_deserialize_with_bad_data(self):
        """ Deserialize a Supplier that has bad data """
        supplier = Supplier()
        self.assertRaises(DataValidationError, supplier.deserialize, "string data")


    def test_save_a_supplier_with_no_name(self):
        """ Save a Supplier with no name """
        supplier = Supplier(None, 2, True, [1, 2, 3], 8.5)
        self.assertRaises(DataValidationError, supplier.save)


    def test_create_a_supplier_with_no_name(self):
        """ Create a Suppleir with no name """
        supplier = Supplier(None, 2, True, [1, 2, 3], 8.5)
        self.assertRaises(DataValidationError, supplier.create)


    def test_find_supplier(self):
        """ Find a Supplier by id """
        Supplier("supplier1", 2, True, [1, 2, 3], 8.5).save()
        # saved_supplier = Supplier("kitty", "cat").save()
        saved_supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        saved_supplier.save()
        supplier = Supplier.find(saved_supplier.id)
        self.assertIsNot(supplier, None)
        self.assertEqual(supplier.id, saved_supplier.id)
        self.assertEqual(supplier.name, "supplier1")


    def test_find_with_no_suppliers(self):
        """ Find a Supplier with empty database """
        supplier = Supplier.find("1")
        self.assertIs(supplier, None)


    def test_supplier_not_found(self):
        """ Find a Supplier that doesnt exist """
        Supplier("supplier1", 2, True, [1, 2, 3], 8.5).save()
        supplier = Supplier.find("2")
        self.assertIs(supplier, None)


    def test_find_by_name(self):
        """ Find a Supplier by Name """
        Supplier("supplier1", 2, True, [1, 2, 3], 8.5).save()
        Supplier("supplier2", 4, False, [1, 3, 5, 7], 6.5).save()
        suppliers = Supplier.find_by_name("supplier1")
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].name, "supplier1")
        self.assertEqual(suppliers[0].like_count, 2)
        self.assertEqual(suppliers[0].is_active, True)
        self.assertEqual(len(suppliers[0].products), 3)
        self.assertEqual(suppliers[0].rating, 8.5)


    def test_find_by_is_active(self):
        """ Find a Supplier by is_active """
        Supplier("supplier1", 2, True, [1, 2, 3], 8.5).save()
        Supplier("supplier2", 4, False, [1, 3, 5, 7], 6.5).save()
        suppliers = Supplier.find_by_is_active(True)
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].name, "supplier1")
        self.assertEqual(suppliers[0].like_count, 2)
        self.assertEqual(suppliers[0].is_active, True)
        self.assertEqual(len(suppliers[0].products), 3)
        self.assertEqual(suppliers[0].rating, 8.5)


    def test_find_by_rating(self):
        """ Find a Supplier by Rating """
        Supplier("supplier1", 2, True, [1, 2, 3], 8.5).save()
        Supplier("supplier2", 4, False, [1, 3, 5, 7], 6.5).save()
        Supplier("supplier3", 6, False, [1, 3, 5], 7.2).save()
        Supplier("supplier4", 8, True, [1, 2, 5], 4.5).save()
        suppliers = Supplier.find_by_greater("rating", 4.2)
        self.assertEqual(len(suppliers), 4)
        suppliers = Supplier.find_by_greater("rating", 7)
        self.assertEqual(len(suppliers), 2)
        suppliers = Supplier.find_by_greater("rating", 8.6)
        self.assertEqual(len(suppliers), 0)
        suppliers = Supplier.find_by_greater("rating", 7.2)
        self.assertEqual(len(suppliers), 1)
        self.assertEqual(suppliers[0].name, "supplier1")
        self.assertEqual(suppliers[0].like_count, 2)
        self.assertEqual(suppliers[0].is_active, True)
        self.assertEqual(suppliers[0].products, [1, 2, 3])
        self.assertEqual(suppliers[0].rating, 8.5)


    @patch('cloudant.database.CloudantDatabase.create_document')
    def test_http_error(self, bad_mock):
        """ Test a Bad Create with HTTP error """
        bad_mock.side_effect = HTTPError()
        supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        supplier.create()
        self.assertIsNone(supplier.id)


    @patch('cloudant.document.Document.exists')
    def test_document_not_exist(self, bad_mock):
        """ Test a Bad Document Exists """
        bad_mock.return_value = False
        supplier = Supplier("supplier1", 2, True, [1, 2, 3], 8.5)
        supplier.create()
        self.assertIsNone(supplier.id)


    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_SERVICES)})
    def test_vcap_services(self):
        """ Test if VCAP_SERVICES works """
        Supplier.init_db("test")
        self.assertIsNotNone(Supplier.client)


    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_NO_SERVICES)})
    def test_vcap_no_services(self):
        """ Test VCAP_SERVICES without Cloudant """
        Supplier.init_db("test")
        self.assertIsNotNone(Supplier.client)
        self.assertIsNotNone(Supplier.database)


    @patch.dict(os.environ, {'VCAP_SERVICES': json.dumps(VCAP_NO_SERVICES),
                             'BINDING_CLOUDANT': json.dumps(BINDING_CLOUDANT)})
    def test_vcap_with_binding(self):
        """ Test no VCAP_SERVICES with BINDING_CLOUDANT """
        Supplier.init_db("test")
        self.assertIsNotNone(Supplier.client)
        self.assertIsNotNone(Supplier.database)


    @patch.dict(os.environ, {'BINDING_CLOUDANT': json.dumps(BINDING_CLOUDANT)})
    def test_vcap_no_services2(self):
        """ Test BINDING_CLOUDANT """
        Supplier.init_db("test")
        self.assertIsNotNone(Supplier.client)
        self.assertIsNotNone(Supplier.database)
