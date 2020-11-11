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
    And I set the "name" to "supplier1"
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
    Then I should see "supplier1" in the "Name" field
    And I should see "10" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "8.7" in the "rating" field
    And I should see "1,2,3" in the "products" field

Scenario: Retrieve a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier2"
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
    Then I should see "supplier2" in the "Name" field
    And I should see "20" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "7.1" in the "rating" field
    And I should see "3,4,8" in the "products" field
    And I should see the message "Success"

Scenario: Like a Supplier
    When I visit the "Home Page"
    And I set the "name" to "supplier1"
    And I set the "like_count" to "10"
    And I select "False" in the "is_active" dropdown
    And I set the "rating" to "8.7"
    And I set the "products" to "1,2,3"
    And I press the "Create" button
    When I copy the "id" field
    And I press the "Clear" button
    Then the "id" field should be empty
    And the "name" field should be empty
    And the "like_count" field should be empty
    And the "rating" field should be empty
    And the "products" field should be empty
    When I paste the "id" field
    And I press the "Like" button
    Then I should see "supplier1" in the "Name" field
    And I should see "11" in the "like_count" field
    And I should see "False" in the "is_active" dropdown
    And I should see "8.7" in the "rating" field
    And I should see "1,2,3" in the "products" field
    And I should see the message "Success"