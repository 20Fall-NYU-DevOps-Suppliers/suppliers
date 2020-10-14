# NYU DevOps Project - Suppliers

###  Project description
The purpose of this project is to develop a suppliers system for an eCommerce web site backend as a collection RESTful services for a client by adopting DevOps methodology.

### Features supported
 Seven paths:
 ------
 GET /suppliers - Returns a list all of the suppliers  
 GET /suppliers/\<string:supplierID\> - Returns the supplier with the given id  
 POST /suppliers - creates a new supplier record in the database  
 PUT /suppliers/\<string:supplierID\> - updates a supplier record in the database  
 DELETE /suppliers/\<string:supplierID\> - deletes a supplier record in the database  
 QUERY /suppliers/ - query the database by the name of the supplier   
 ACTION /suppliers/\<string:supplierId\>/like - increments the like_counter of a supplier 

\<string:supplierID\> is a string of 24 hexadecimal characters eg: 4f4381f4e779897a2c000009

### Running Tests
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

### Running Pylint:
```
vagrant up
vagrant ssh
cd /vagrant
pylint --rcfile=pylint.conf service/*.py
pylint --rcfile=pylint.conf tests/*.py
````

