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
import logging
from flask import jsonify, request, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from service.models import Supplier
from . import app

# Error handlers require app to be initialized so we must import
# them only after we have initialized the Flask app instance
import service.error_handlers

@app.route('/')
def hello():
    """
    Test the '/' path
    """
    return "Hello Supplier!"

######################################################################
# RETRIEVE A SUPPLIER (READ)
######################################################################
@app.route('/suppliers/<supplier_id>', methods=['GET'])
def get_suppliers(supplier_id):
    """
    Retrieve a single Supplier
    This endpoint will return a Supplier based on it's id
    """
    app.logger.info("Request to Retrieve a supplier with id [%s]", supplier_id)
    supplier = Supplier.find(supplier_id)
    if not supplier:
        raise NotFound("Supplier with id '{}' was not found.".format(supplier_id))
    return make_response(jsonify(supplier.serialize()), status.HTTP_200_OK)


######################################################################
# CREATE A NEW SUPPLIER
######################################################################
@app.route('/suppliers', methods=['POST'])
def create_suppliers():
    """
    Creates a Supplier
    This endpoint will create a Supplier based the data in the body that is posted
    """
    app.logger.info('Request to Create a Supplier...')
    data = {}
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
    app.logger.info(data)
    supplier = Supplier()
    supplier.deserialize(data)
    supplier.save()
    app.logger.info('Supplier with new id [%s] saved!', supplier.id)
    message = supplier.serialize()
    # TODO after finishing Query and add utility functions
    # location_url = url_for('get_suppliers', supplier_id=supplier.id, _external=True)
    # return make_response(jsonify(message), status.HTTP_201_CREATED,
    #                       {'Location': location_url})
    return make_response(jsonify(message), status.HTTP_201_CREATED)


######################################################################
# LIST ALL PETS
######################################################################
@app.route('/suppliers', methods=['GET'])
def list_suppliers():
    """ Returns all of the suppliers """
    app.logger.info("Request for supplier list")
    suppliers = Supplier.all()

    results = [supplier.serialize() for supplier in suppliers]
    app.logger.info("Returning %d suppliers", len(results))
    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
#  ACTION LIKE A SUPPLIER
######################################################################
@app.route('/suppliers/<supplier_id>/like', methods=['PUT'])
def like_supplier(supplier_id):
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
    message = supplier.serialize()
    return make_response(jsonify(message), status.HTTP_200_OK)


######################################################################
# DELETE A SUPPLIER
######################################################################
@app.route('/suppliers/<supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """
    Delete a Supplier
    This endpoint will delete a Supplier based the id specified in the path
    """
    app.logger.info('Request to Delete a Supplier with id [%s]', supplier_id)
    supplier = Supplier.find(supplier_id)
    if supplier:
        supplier.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

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
