"""
Supplier Store Service

Paths:
------
GET /suppliers - Returns a list all of the Suppliers
GET /suppliers/{id} - Returns the Supplier with a given id number
POST /suppliers - creates a new Supplier record in the database
PUT /suppliers/{id} - updates a Supplier record in the database
DELETE /suppliers/{id} - deletes a Supplier record in the database
TODO Query and Action Paths
"""

import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from service.models import Supplier
from . import app

# Error handlers require app to be initialized so we must import
# them only after we have initialized the Flask app instance
import service.error_handlers

@app.route('/')
def hello():
    return "Hello Supplier!"


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
    #location_url = url_for('get_suppliers', supplier_id=supplier.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED)
    # return make_response(jsonify(message), status.HTTP_201_CREATED,
    #                      {'Location': location_url})




######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


@app.before_first_request
def init_db(dbname="suppliers"):
    """ Initlaize the model """
    Supplier.init_db(dbname)

# load sample data
def data_load(payload):
    """ Loads a Supplier into the database """
    supplier = Supplier(payload['name'], payload['is_active'], payload['like_count'], payload['products'], payload['rating'])
    supplier.save()

def data_reset():
    """ Removes all Suppliers from the database """
    Supplier.remove_all()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if 'Content-Type' not in request.headers:
        app.logger.error('No Content-Type specified.')
        abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

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
