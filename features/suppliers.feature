Feature: The supplier service back-end
    As a Supplier Manager
    I need a RESTful catalog service
    So that I can keep track of all my suppliers

Background:
    Given the following suppliers
        | name       | like_count | is_active | products | rating |
        | supplier1  | 10         | true      | 1,2,3    | 5.6    |
        | supplier2  | 20     	  | true      | 1,4,5	 | 4.8    |
        | supplier3  | 30         | false     | 2,3,6    | 7.5    |
        | supplier4  | 40         | true      | 4,5,7    | 9.0    |


Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Supplier Demo RESTful Service" in the title
    And I should not see "404 Not Found"

Scenario: Create a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier5"
    And I set the "like_count" to "10"
    And I select "False" in the "is_active" dropdown
    And I set the "rating" to "8.7"
    And I set the "products" to "1,2,3"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "name" field should be empty
    And the "like_count" field should be empty
    And the "rating" field should be empty
    And the "products" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "supplier5" in the "name" field
    And I should see "10" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "8.7" in the "rating" field
    And I should see "1,2,3" in the "products" field

Scenario: Retrieve a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier6"
    And I set the "like_count" to "20"
    And I select "False" in the "is_active" dropdown
    And I set the "rating" to "7.1"
    And I set the "products" to "3,4,8"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "name" field should be empty
    And the "like_count" field should be empty
    And the "rating" field should be empty
    And the "products" field should be empty
    When I paste the "id" field
    And I press the "Retrieve" button
    Then I should see "supplier6" in the "name" field
    And I should see "20" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "7.1" in the "rating" field
    And I should see "3,4,8" in the "products" field
    And I should see the message "Success"

Scenario: Like a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier1"
    And I press the "Search" button
    Then I should see "supplier1" in the "name" field
    And I should see "10" in the "like_count" field
    And I should see "True" in the "is_active" dropdown
    And I should see "5.6" in the "rating" field
    And I should see "1,2,3" in the "products" field
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Like" button
    Then I should see "supplier1" in the "name" field
    And I should see "11" in the "like_count" field
    And I should see "True" in the "is_active" dropdown
    And I should see "5.6" in the "rating" field
    And I should see "1,2,3" in the "products" field
    And I should see the message "Success"

Scenario: List all Suppliers
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "supplier1" in the results
    And I should see "supplier2" in the results
    And I should not see "supplier3" in the results
    And I should see "supplier4" in the results

Scenario: Update a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier1"
    And I press the "Search" button
    Then I should see "supplier1" in the "name" field
    And I should see "10" in the "like_count" field
    And I should see "True" in the "is_active" dropdown
    And I should see "5.6" in the "rating" field
    And I should see "1,2,3" in the "products" field
    When I change "name" to "supplier5"
    And I change "like_count" to "13"
    And I select "False" in the "is_active" dropdown 
    And I change "rating" to "4.3"
    And I change "products" to "1,2,3,4,5"
    And I press the "Update" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "supplier5" in the "name" field
    And I should see "13" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "4.3" in the "rating" field
    And I should see "1,2,3,4,5" in the "products" field
    When I press the "Clear" button
    And I press the "Search" button
    Then I should see "supplier5" in the results
    And I should not see "supplier1" in the results

Scenario: Query for Suppliers
    When I visit the "Home Page"
    And I set the "name" to "supplier1"
    And I press the "Search" button
    Then I should see "supplier1" in the "name" field
    And I should see "10" in the "like_count" field
    And I should see "True" in the "is_active" dropdown
    And I should see "5.6" in the "rating" field
    And I should see "1,2,3" in the "products" field
    When I press the "Clear" button
    And I change "like_count" to "25"
    And I press the "Search" button
    Then I should see "supplier3" in the results
    And I should see "supplier4" in the results
    And I should not see "supplier1" in the results
    And I should not see "supplier2" in the results
    When I press the "Clear" button
    And I select "True" in the "is_active" dropdown
    And I press the "Search" button
    Then I should see "supplier1" in the results
    And I should see "supplier2" in the results
    And I should see "supplier4" in the results
    And I should not see "supplier3" in the results
    When I press the "Clear" button
    And I change "rating" to "6.2"
    And I press the "Search" button
    Then I should see "supplier3" in the results
    And I should see "supplier4" in the results
    And I should not see "supplier1" in the results
    And I should not see "supplier2" in the results
    When I press the "Clear" button
    And I change "products" to "5"
    And I press the "Search" button
    Then I should see "supplier2" in the results
    And I should see "supplier4" in the results
    And I should not see "supplier1" in the results
    And I should not see "supplier3" in the results

Scenario: Delete a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier6"
    And I set the "like_count" to "15"
    And I select "False" in the "is_active" dropdown
    And I set the "rating" to "9.0"
    And I set the "products" to "1,2,3,4"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "name" field should be empty
    And the "like_count" field should be empty
    And the "rating" field should be empty
    And the "products" field should be empty
    When I paste the "id" field
    And I press the "Delete" button
    Then I should see the message "Supplier has been Deleted!"
    When I press the "Clear" button
    And I press the "Search" button
    Then I should not see "supplier6" in the results

Scenario: Recommend a Supplier
   When I visit the "Home Page"
   And I set the "name" to "supplier8"
   And I set the "like_count" to "15"
   And I select "True" in the "is_active" dropdown
   And I set the "rating" to "6.0"
   And I set the "products" to "4"
   And I press the "Create" button
   Then I should see the message "Success"
   When I set the "name" to "supplier9"
   And I set the "like_count" to "15"
   And I select "True" in the "is_active" dropdown
   And I set the "rating" to "15.0"
   And I set the "products" to "4"
   And I press the "Create" button
   Then I should see the message "Success"
   When I press the "Clear" button
   Then the "id" field should be empty
   And the "name" field should be empty
   And the "like_count" field should be empty
   And the "rating" field should be empty
   And the "products" field should be empty
   When I set the "products" to "4"
   And I press the "Recommend" button
   Then I should see "supplier9" in the results
   And I should see the message "Success"
  


