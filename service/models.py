"""
Model file that defines the data schema for suppliers and related eddatabase operations
"""

"""
Supplier Model is defined using Cloudant

You must initlaize this class before use by calling inititlize().
This class looks for an environment variable called VCAP_SERVICES
to get it's database credentials from. If it cannot find one, it
tries to connect to Cloudant on the localhost. If that fails it looks
for a server name 'cloudant' to connect to.

To use with Docker couchdb database use:
    docker run -d --name couchdb -p 5984:5984 -e COUCHDB_USER=admin -e COUCHDB_PASSWORD=pass couchdb
"""


"""
Attributes in a Supplier:
-----------
id (int) - the supplier Id
name (string) - the supplier name
like_count (int) - the number of like given by customer
is_active (boolean) - indicate whether the supplier is active or not
products (list of int) - a list of product id provied by this supplier
rating (float) - average rating given by customer, 0-10 (eg 7.8)

"""

import os
import json
import logging
from cloudant.client import Cloudant
from cloudant.query import Query
from cloudant.adapters import Replay429Adapter
from requests import HTTPError, ConnectionError

# get configruation from enviuronment (12-factor)
ADMIN_PARTY = os.environ.get('ADMIN_PARTY', 'False').lower() == 'true'
CLOUDANT_HOST = os.environ.get('CLOUDANT_HOST', 'localhost')
CLOUDANT_USERNAME = os.environ.get('CLOUDANT_USERNAME', 'admin')
CLOUDANT_PASSWORD = os.environ.get('CLOUDANT_PASSWORD', 'pass')

# global variables for retry (must be int)
RETRY_COUNT = int(os.environ.get('RETRY_COUNT', 10))
RETRY_DELAY = int(os.environ.get('RETRY_DELAY', 1))
RETRY_BACKOFF = int(os.environ.get('RETRY_BACKOFF', 2))


class DatabaseConnectionError(Exception):
    """ Custom Exception when database connection fails """
    pass

class DataValidationError(Exception):
    """ Custom Exception with data validation fails """
    pass


class Supplier(object):
    """
    Class that represents a Supplier

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)
    client = None   # cloudant.client.Cloudant
    database = None # cloudant.database.CloudantDatabase

    def __init__(self, name=None, like_count=None, is_active=True, products=None, rating=None):
        """ Constructor """
        if products is None:
            products = []
        self.id = None
        self.name = name
        self.like_count = like_count
        self.is_active = is_active
        self.products = products
        self.rating = rating
    
    def create(self):
        """
        Creates a new Supplier in the database
        """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')

        try:
            document = self.database.create_document(self.serialize())
        except HTTPError as err:
            Supplier.logger.warning('Create failed: %s', err)
            return

        if document.exists():
            self.id = document['_id']
    
    def update(self):
        """ Updates a Supplier in the database """
        try:
            document = self.database[self.id]
        except KeyError:
            document = None
        if document:
            document.update(self.serialize())
            document.save()


    def save(self):
        """ Saves a Supplier in the database """
        if self.name is None:   # name is the only required field
            raise DataValidationError('name attribute is not set')
        if self.id:
            self.update()
        else:
            self.create()


    def serialize(self):
        """ serializes a Supplier into a dictionary """
        supplier = {
            "name": self.name,
            "like_count": self.like_count,
            "is_active": self.is_active,
            "products": self.products,
            "rating": self.rating
        }
        if self.id:
            supplier['_id'] = self.id
        return supplier


    def deserialize(self, data):
        """ deserializes a Supplier my marshalling the data.

        :param data: a Python dictionary representing a Supplier.
        """
        Supplier.logger.info('deserialize(%s)', data)
        try:
            self.name = data['name']
            self.like_count = data['like_count']
            self.is_active = data['is_active']
            self.products = data['products']
            self.rating = data['rating']
        except KeyError as error:
            raise DataValidationError('Invalid supplier: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid supplier: body of request contained bad or no data')

        # if there is no id and the data has one, assign it
        if not self.id and '_id' in data:
            self.id = data['_id']

        return self



######################################################################
#  S T A T I C   D A T A B S E   M E T H O D S
######################################################################
    
    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        for document in cls.database:
            document.delete()
    
    @classmethod
    def all(cls):
        """ Query that returns all Suppliers """
        results = []
        for doc in cls.database:
            supplier = Supplier().deserialize(doc)
            supplier.id = doc['_id']
            results.append(supplier)
        return results
    
######################################################################
#  F I N D E R   M E T H O D S
######################################################################

    @classmethod
    def find(cls, supplier_id):
        """ Query that finds Suppliers by their id """
        try:
            document = cls.database[supplier_id]
            return Supplier().deserialize(document)
        except KeyError:
            return None


############################################################
#  C L O U D A N T   D A T A B A S E   C O N N E C T I O N
############################################################

    @staticmethod
    def init_db(dbname='suppliers'):
        """
        Initialized Coundant database connection
        """
        opts = {}
        # Try and get VCAP from the environment
        if 'VCAP_SERVICES' in os.environ:
            Supplier.logger.info('Found Cloud Foundry VCAP_SERVICES bindings')
            vcap_services = json.loads(os.environ['VCAP_SERVICES'])
            # Look for Cloudant in VCAP_SERVICES
            for service in vcap_services:
                if service.startswith('cloudantNoSQLDB'):
                    opts = vcap_services[service][0]['credentials']

        # if VCAP_SERVICES isn't found, maybe we are running on Kubernetes?
        if not opts and 'BINDING_CLOUDANT' in os.environ:
            Supplier.logger.info('Found Kubernetes BINDING_CLOUDANT bindings')
            opts = json.loads(os.environ['BINDING_CLOUDANT'])

        # If Cloudant not found in VCAP_SERVICES or BINDING_CLOUDANT
        # get it from the CLOUDANT_xxx environment variables
        if not opts:
            Supplier.logger.info('VCAP_SERVICES and BINDING_CLOUDANT undefined.')
            opts = {
                "username": CLOUDANT_USERNAME,
                "password": CLOUDANT_PASSWORD,
                "host": CLOUDANT_HOST,
                "port": 5984,
                "url": "http://"+CLOUDANT_HOST+":5984/"
            }

        if any(k not in opts for k in ('host', 'username', 'password', 'port', 'url')):
            raise DatabaseConnectionError('Error - Failed to retrieve options. ' \
                             'Check that app is bound to a Cloudant service.')

        Supplier.logger.info('Cloudant Endpoint: %s', opts['url'])
        try:
            if ADMIN_PARTY:
                Supplier.logger.info('Running in Admin Party Mode...')
            Supplier.client = Cloudant(opts['username'],
                                  opts['password'],
                                  url=opts['url'],
                                  connect=True,
                                  auto_renew=True,
                                  admin_party=ADMIN_PARTY,
                                  adapter=Replay429Adapter(retries=10, initialBackoff=0.01)
                                 )

        except ConnectionError:
            raise DatabaseConnectionError('Cloudant service could not be reached')

        # Create database if it doesn't exist
        try:
            Supplier.database = Supplier.client[dbname]
        except KeyError:
            # Create a database using an initialized client
            Supplier.database = Supplier.client.create_database(dbname)
        # check for success
        if not Supplier.database.exists():
            raise DatabaseConnectionError('Database [{}] could not be obtained'.format(dbname))
