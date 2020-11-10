"""
Supplier Steps

Steps file for suppliers.feature

"""

from os import getenv
import logging
import json
import requests
from behave import *
from compare import expect, ensure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions

WAIT_SECONDS = int(getenv('WAIT_SECONDS', '60'))
ID_PREFIX = 'supplier_'


@given('the following suppliers')
def step_impl(context):
    """ Delete all Suppliers and load new ones """
    headers = {'Content-Type': 'application/json'}
    # list all of the suppliers and delete them one by one
    context.resp = requests.get(context.base_url + '/suppliers', headers=headers)
    expect(context.resp.status_code).to_equal(200)
    for supplier in context.resp.json():
        context.resp = requests.delete(context.base_url + '/suppliers/' + str(supplier["_id"]), headers=headers)
        expect(context.resp.status_code).to_equal(204)

    # load the database with new suppliers
    create_url = context.base_url + '/suppliers'
    for row in context.table:
        products = [int(product) for product in row['products'].split(",")]
        data = {
            "name": row['name'],
            "like_count": int(row['like_count']),
            "is_active": row['is_active'] in ['True', 'true', '1'],
            "products": products,
            "rating": float(row['rating'])
        }
        payload = json.dumps(data)
        context.resp = requests.post(create_url, data=payload, headers=headers)
        expect(context.resp.status_code).to_equal(201)


@when('I visit the "Home Page"')
def step_impl(context):
    """ Make a call to the base URL """
    context.driver.get(context.base_url)


@then('I should see "{message}" in the title')
def step_impl(context, message):
    """ Check the document title for a message """
    expect(context.driver.title).to_contain(message)


@then('I should not see "{message}"')
def step_impl(context, message):
    error_msg = "I should not see '%s' in '%s'" % (message, context.resp.text)
    ensure(message in context.resp.text, False, error_msg)
