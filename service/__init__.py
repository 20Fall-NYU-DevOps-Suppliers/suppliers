from flask import Flask


"""
Package: app
Package for the application models and services
This module also sets up the logging
"""
import os
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)

# Load Configurations
app.config.from_object('config')

# Import the service After the Flask app is created
from service import service, models

# Set up logging for production
print("Setting up logging for {}...".format(__name__))
app.logger.propagate = False
if __name__ != "__main__":
    gunicorn_logger = logging.getLogger("gunicorn.error")
    if gunicorn_logger:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    app.logger.info("Logging established")

app.logger.info(70 * "*")
app.logger.info("  S U P P L I E R S   S E R V I C E   R U N N I N G  ".center(70, "*"))
print("  S U P P L I E R S   S E R V I C E   R U N N I N G  ")
app.logger.info(70 * "*")

app.logger.info('Service inititalized!')

# TODO Initialize DB
