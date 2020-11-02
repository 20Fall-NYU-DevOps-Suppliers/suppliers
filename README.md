# NYU DevOps Project - Suppliers
[![Build Status](https://travis-ci.org/20Fall-NYU-DevOps-Suppliers/suppliers.svg?branch=master)](https://travis-ci.org/20Fall-NYU-DevOps-Suppliers/suppliers)
[![codecov](https://codecov.io/gh/20Fall-NYU-DevOps-Suppliers/suppliers/branch/master/graph/badge.svg)](https://codecov.io/gh/20Fall-NYU-DevOps-Suppliers/suppliers)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

###  Project description
The purpose of this project is to develop a suppliers system for an eCommerce web site backend as a collection RESTful services for a client by adopting DevOps methodology.


## API Documentation

### Model description

|  Column  |  Type  |
| :----------: | :---------: |
| supplier_id | String |
| name | String |
| like_count | Integer |
| is_active | Boolean |
| products | List of Integers |
| rating | Float | 

### URLs
| HTTP Method | URL | Description | Return
| :--- | :--- | :--- | :--- |
| `GET` | `/suppliers/{id}` | Get Supplier by ID | Supplier Object
| `GET` | `/suppliers` | Returns a list of all the Suppliers | Supplier Object
| `POST` | `/suppliers` | Creates a new Supplier record in the database | Supplier Object
| `PUT` | `/suppliers/{id}` | Updates a Supplier record in the database | Supplier Object
| `GET` | `/suppliers` | Returns a list of all the Suppliers | Supplier Object
| `PUT` | `/suppliers/{id}/like` | Increment the like count of the Supplier with the given id number | Supplier Object
| `DELETE` | `/suppliers/{id}` | Delete the Supplier with the given id number | 204 Status Code 

\<supplierID\> is a string of 24 hexadecimal characters eg: 1e8392f4e6752990a2c23789

### Manually Running The Tests
To run the TDD tests please run the following commands:
```
 git clone https://github.com/20Fall-NYU-DevOps-Suppliers/suppliers.git
 cd suppliers
 vagrant up
 vagrant ssh
 cd /vagrant
 nosetests
```

### Running the Flask App:
```
 vagrant up
 vagrant ssh
 cd /vagrant
 FLASK_APP=service:app flask run -h 0.0.0.0
```

Then the service will available at: http://0.0.0.0:5000/suppliers

### Checking The Pylint Score:
```
vagrant up
vagrant ssh
cd /vagrant
pylint --rcfile=pylint.conf service/*.py
pylint --rcfile=pylint.conf tests/*.py
