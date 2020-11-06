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
    Then I should see "Hello Supplier!" in the title
    And I should not see "404 Not Found"