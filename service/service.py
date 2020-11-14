"""
Supplier Store Service

Paths:
------
GET /suppliers - Returns a list all of the Suppliers
GET /suppliers/{id} - Returns the Supplier with a given id number
POST /suppliers - creates a new Supplier record in the database
PUT /suppliers/{id} - updates a Supplier record in the database
DELETE /suppliers/{id} - deletes a Supplier record in the database
ACTION /suppliers/{id}/like - increments the like count of the Supplier
"""

import sys
import uuid
import logging
from functools import wraps
from flask import jsonify, request, make_response, abort, url_for
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields, reqparse, inputs, apidoc
from werkzeug.exceptions import NotFound
from service.models import Supplier, DataValidationError, DatabaseConnectionError
from . import app

# Error handlers require app to be initialized so we must import
# them only after we have initialized the Flask app instance


# Document the type of autorization required
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-Api-Key'
    }
}


######################################################################
# GET HOME PAGE
######################################################################
@app.route('/')
def index():
    """ Render Home Page"""
    return app.send_static_file('index.html')


######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Supplier Demo REST API Service',
          description='This is a sample server Supplier store server.',
          default='Suppliers',
          default_label='Supplier shop operations',
          doc='/apidocs', # default also could use doc='/apidocs/'
          authorizations=authorizations
         )


# Define the model so that the docs reflect what can be sent
supplier_model = api.model('Supplier', {
    '_id': fields.String(readOnly = True,
                         description='The unique id assigned internally by service'),
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'like_count': fields.Integer(required=False,
                                 description='The like count of the Supplier'),
    'is_active': fields.Boolean(required=False,
                                description='Is the Supplier active?'),
    'rating': fields.Float(required=False,
                           description='The rating of the Supplier'),
    'products': fields.List(fields.Integer,required=False,
                              description='List of products the Supplier provide')
})


create_model = api.model('Supplier', {
    'name': fields.String(required=True,
                          description='The name of the Supplier'),
    'like_count': fields.Integer(required=False,
                                 description='The like count of the Supplier'),
    'is_active': fields.Boolean(required=False,
                                description='Is the Supplier active?'),
    'rating': fields.Float(required=False,
                           description='The rating of the Supplier'),
    'products': fields.List(fields.Integer,required=False,
                              description='List of products the Supplier provide')
})


# query string arguments
supplier_args = reqparse.RequestParser()
supplier_args.add_argument('name', type=str, required=False, help='List Suppliers by name')
supplier_args.add_argument('like_count', type=int, required=False, help='List Suppliers by like_count')
supplier_args.add_argument('is_active', type=bool, required=False, help='List Suppliers by is_active')
supplier_args.add_argument('rating', type=float, required=False, help='List Suppliers by rating')
supplier_args.add_argument('product_id', type=int, required=False, help='List Suppliers by product_id')


######################################################################
# Special Error Handlers
######################################################################
@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    message = str(error)
    app.logger.error(message)
    return {
        'status_code': status.HTTP_400_BAD_REQUEST,
        'error': 'Bad Request',
        'message': message
    }, status.HTTP_400_BAD_REQUEST


@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = str(error)
    app.logger.critical(message)
    return {
        'status_code': status.HTTP_503_SERVICE_UNAVAILABLE,
        'error': 'Service Unavailable',
        'message': message
    }, status.HTTP_503_SERVICE_UNAVAILABLE


######################################################################
# Authorization Decorator
######################################################################
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = None
#         if 'X-Api-Key' in request.headers:
#             token = request.headers['X-Api-Key']
#
#         if app.config.get('API_KEY') and app.config['API_KEY'] == token:
#             return f(*args, **kwargs)
#         else:
#             return {'message': 'Invalid or missing token'}, 401
#     return decorated


######################################################################
# Function to generate a random API key (good for testing)
######################################################################
def generate_apikey():
    """ Helper function used when testing API keys """
    return uuid.uuid4().hex


######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)


######################################################################
# GET API DOCS
######################################################################
@app.route('/apidocs')
def apidoc_page():
    """API Documentation Page"""
    return apidoc.ui_for(api)


######################################################################
#  PATH: /suppliers/{id}
######################################################################
@api.route('/suppliers/<supplier_id>')
@api.param('supplier_id', 'The Supplier identifier')
class SupplierResource(Resource):
    """
    SupplierResource class
    Allows the manipulation of a single Supplier
    GET /suppliers/{id} - Returns a Supplier with the id
    PUT /suppliers/{id} - Update a Supplier with the id
    DELETE /suppliers/{id} -  Deletes a Supplier with the id
    """

    #------------------------------------------------------------------
    # RETRIEVE A SUPPLIER
    #------------------------------------------------------------------
    @api.doc('get_suppliers')
    @api.response(404, 'Supplier not found')
    # @api.marshal_with(supplier_model)
    def get(self, supplier_id):
        """
        Retrieve a single Supplier
        This endpoint will return a Supplier based on it's id
        """
        app.logger.info("Request to Retrieve a supplier with id [%s]", supplier_id)
        supplier = Supplier.find(supplier_id)
        if not supplier:
            api.abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' was not found.".format(supplier_id))
        return supplier.serialize(), status.HTTP_200_OK


    #------------------------------------------------------------------
    # UPDATE AN EXISTING SUPPLIER
    #------------------------------------------------------------------
    @api.doc('update_suppliers', security='apikey')
    @api.response(404, 'Supplier not found')
    @api.response(400, 'The posted Supplier data was not valid')
    @api.expect(supplier_model)
    # @api.marshal_with(supplier_model)
    def put(self, supplier_id):
        """
        Update a supplier
        This endpoint will update a Supplier based the body that is posted
        """
        app.logger.info('Request to Update a supplier with id [%s]', supplier_id)
        check_content_type('application/json')
        supplier = Supplier.find(supplier_id)
        if not supplier:
            return api.abort(status.HTTP_404_NOT_FOUND, "Supplier with id '{}' not found".format(supplier_id))

        data = request.get_json()
        # Data type transfer
        data = data_type_transfer(data)

        app.logger.info(data)
        supplier.deserialize(data)
        supplier.id = supplier_id
        supplier.save()
        return supplier.serialize(), status.HTTP_200_OK


    #------------------------------------------------------------------
    # DELETE A PET
    #------------------------------------------------------------------
    @api.doc('delete_pets', security='apikey')
    @api.response(204, 'Pet deleted')
    def delete(self, supplier_id):
        """
        Delete a Supplier
        This endpoint will delete a Supplier based the id specified in the path
        """
        app.logger.info('Request to Delete a Supplier with id [%s]', supplier_id)
        supplier = Supplier.find(supplier_id)
        if supplier:
            supplier.delete()
            app.logger.info("Supplier with ID [%s] delete complete.", supplier_id)
        else:
            app.logger.info("Supplier with ID [%s] does not exist.", supplier_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /suppliers
######################################################################
@api.route('/suppliers', strict_slashes = True)
class SupplierCollection(Resource):
    """ Handles all interactions with collections of Suppliers """
    #------------------------------------------------------------------
    # LIST ALL SUPPLIERS
    #------------------------------------------------------------------
    @api.doc('list_pets')
    @api.response(400, 'Bad Request')
    @api.expect(supplier_args, validate=True)
    # @api.marshal_list_with(supplier_model)
    def get(self):
        """ Returns all of the suppliers """
        app.logger.info('Request to list Suppliers...')

        name = request.args.get('name')
        is_active = request.args.get('is_active')
        rating = request.args.get('rating')
        product_id = request.args.get('product_id')
        like_count = request.args.get('like_count')

        if name:
            app.logger.info('Find suppliers by name: %s', name)
            suppliers = Supplier.find_by_name(name)
        elif like_count:
            app.logger.info('Find suppliers with rating greater than: %s', rating)
            like_count = int(like_count)
            suppliers = Supplier.find_by_greater("like_count", like_count)
        elif is_active:
            app.logger.info('Find suppliers by is_active: %s', is_active)
            is_active = (is_active == 'true')
            suppliers = Supplier.find_by_is_active(is_active)
        elif rating:
            app.logger.info('Find suppliers with rating greater than: %s', rating)
            rating = float(rating)
            suppliers = Supplier.find_by_greater("rating", rating)
        elif product_id:
            app.logger.info('Find suppliers containing product with id %s in their products',
                            product_id)
            product_id = int(product_id)
            suppliers = [supplier for supplier in Supplier.all() if product_id in supplier.products]
        else:
            app.logger.info('Find all suppliers')
            suppliers = Supplier.all()

        app.logger.info('[%s] Suppliers returned', len(suppliers))
        results = [supplier.serialize() for supplier in suppliers]
        app.logger.info("Returning %d suppliers", len(results))
        return results, status.HTTP_200_OK


    #------------------------------------------------------------------
    # ADD A NEW SUPPLIER
    #------------------------------------------------------------------
    @api.doc('create_suppliers', security='apikey')
    @api.expect(create_model)
    @api.response(400, 'The posted data was not valid')
    @api.response(201, 'Supplier created successfully')
    # @api.marshal_with(supplier_model, code=201)
    def post(self):
        """
        Creates a Supplier
        This endpoint will create a Supplier based the data in the body that is posted
        """
        app.logger.info('Request to Create a Supplier...')

        # Check for form submission data
        if request.headers.get('Content-Type') == 'application/x-www-form-urlencoded':
            app.logger.info('Getting data from form submit')
            data = {
                "name": request.form['name'],
                "like_count": request.form['like_count'],
                "is_active": request.form['is_active'],
                "products": request.form['products'],
                "rating": request.form['rating']
            }
        else:
            check_content_type('application/json')
            app.logger.info('Getting json data from API call')
            data = request.get_json()
            # Data type transfer
            data = data_type_transfer(data)

        app.logger.info(data)
        supplier = Supplier()
        supplier.deserialize(data)
        supplier.save()
        app.logger.info('Supplier with new id [%s] saved!', supplier.id)
        location_url = api.url_for(SupplierResource, supplier_id=supplier.id, _external=True)
        return supplier.serialize(), status.HTTP_201_CREATED, {'Location': location_url}


######################################################################
# PATH: /suppliers/{supplier_id}/like
######################################################################
@api.route('/suppliers/<supplier_id>/like')
class SupplierAction(Resource):
    @api.doc('like_suppliers')
    @api.response(404, 'Supplier not found')
    def put(self, supplier_id):
        """
        Like a single Supplier
        This endpoint will update the like_count of the Supplier based on it's id in the database
        """
        supplier = Supplier.find(supplier_id)
        if not supplier:
            raise NotFound("Supplier with id '{}' was not found.".format(supplier_id))
        supplier.like_count += 1
        supplier.save()
        app.logger.info('You liked supplier with id [%s]!', supplier.id)
        return supplier.serialize(), status.HTTP_200_OK


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


@app.before_first_request
def init_db(dbname="suppliers"):
    """ Initlaize the model """
    Supplier.init_db(dbname)


def data_reset():
    """ Removes all Suppliers from the database """
    Supplier.remove_all()


def data_type_transfer(data):
    """ Transfer string fields in submitted json data if necessary """
    if isinstance(data['is_active'], str):
        data['is_active'] = data['is_active'] in ["true", "True", "1"]
    if data['like_count']: data['like_count'] = int(data['like_count'])
    if isinstance(data['products'], str):
        if data['products']:
            data['products'] = [int(i) for i in data['products'].split(',') if i]
        else:
            data['products'] = []
    if data['rating']: data['rating'] = float(data['rating'])
    return data


def check_content_type(content_type):
    """ Checks that the media type is correct """
    if 'Content-Type' not in request.headers:
        app.logger.error('No Content-Type specified.')
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
              'Content-Type must be {}'.format(content_type))

    if request.headers['Content-Type'] == content_type:
        return

    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))


#@app.before_first_request
def initialize_logging(log_level=app.config['LOGGING_LEVEL']):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')
