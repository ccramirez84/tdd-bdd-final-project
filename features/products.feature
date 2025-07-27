Feature: The product store service back-end
    As a Product Store Owner
    I need a RESTful catalog service
    So that I can keep track of all my products

Background:
    Given the following products
        | name       | description       | price   | available | category   |
        | Hat        | A red fedora      | 59.95   | True      | CLOTHS     |
        | Shoes      | Blue shoes        | 120.50  | False     | CLOTHS     |
        | Big Mac    | 1/4 lb burger     | 5.99    | True      | FOOD       |
        | Sheets     | Full bed sheets   | 87.00   | True      | HOUSEWARES |
        | Hammer     | Claw hammer       | 34.95   | True      | TOOLS      |
        | Wrench     | Adjustable wrench | 25.00   | True      | TOOLS      |
        | Apple      | Red fruit         | 1.50    | True      | FOOD       |
        | Banana     | Yellow fruit      | 0.75    | True      | FOOD       |
        | Car Wax    | Car polish        | 15.00   | True      | AUTOMOTIVE |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Product Catalog Administration" in the title
    And I should not see "404 Not Found"

Scenario: Create a Product
    When I visit the "Home Page"
    And I set the "Name" to "Hammer"
    And I set the "Description" to "Claw hammer"
    And I select "True" in the "Available" dropdown
    And I select "Tools" in the "Category" dropdown
    And I set the "Price" to "34.95"
    And I press the "Create" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    And the "Description" field should be empty
    And the "Available" dropdown should be "True"
    And the "Category" dropdown should be "UNKNOWN"
    And the "Price" field should be empty
    When I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hammer" in the "Name" field
    And I should see "Claw hammer" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "Tools" in the "Category" dropdown
    And I should see "34.95" in the "Price" field

Scenario: Leer un Producto
    When I visit the "Home Page"
    And I set the "Name" to "Hat"
    And I press the "Search" button
    Then I should see the message "Success"
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    And I should see "True" in the "Available" dropdown
    And I should see "CLOTHS" in the "Category" dropdown
    And I should see "59.95" in the "Price" field

Scenario: Retrieve a Product
    Given a product with name "Hat"
    When I visit the "Home Page"
    And I set the "Id" field to the ID of "Hat"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Hat" in the "Name" field
    And I should see "A red fedora" in the "Description" field
    And I should see "59.95" in the "Price" field
    And I should see "True" in the "Available" dropdown
    And I should see "CLOTHS" in the "Category" dropdown

Scenario: Retrieve a Product not found
    When I visit the "Home Page"
    And I set the "Id" field to "99999"
    And I press the "Retrieve" button
    Then I should see the message "Product with id '99999' was not found."

Scenario: Update a Product
    Given a product with name "Big Mac"
    When I visit the "Home Page"
    And I set the "Id" field to the ID of "Big Mac"
    And I press the "Retrieve" button
    Then I should see the message "Success"
    And I should see "Big Mac" in the "Name" field
    And I set the "Description" to "Double Quarter Pounder"
    And I set the "Price" to "7.99"
    And I select "False" in the "Available" dropdown
    And I press the "Update" button
    Then I should see the message "Success"
    And I should see "Big Mac" in the "Name" field
    And I should see "Double Quarter Pounder" in the "Description" field
    And I should see "7.99" in the "Price" field
    And I should see "False" in the "Available" dropdown
    When I copy the "Id" field
    And I press the "Clear" button
    And I paste the "Id" field
    And I press the "Retrieve" button
    Then I should see "Big Mac" in the "Name" field
    And I should see "Double Quarter Pounder" in the "Description" field
    And I should see "7.99" in the "Price" field
    And I should see "False" in the "Available" dropdown

Scenario: Delete a Product
    Given a product with name "Shoes"
    When I visit the "Home Page"
    And I set the "Id" field to the ID of "Shoes"
    And I press the "Delete" button
    Then I should see the message "Product has been Deleted"
    When I press the "Clear" button
    And I set the "Id" field to the ID of "Shoes"
    And I press the "Retrieve" button
    Then I should see the message "Product with id"

Scenario: List all Products
    When I visit the "Home Page"
    And I press the "Search" button
    Then I should see "Hat" in the results
    And I should see "Shoes" in the results
    And I should see "Big Mac" in the results
    And I should see "Sheets" in the results
    And I should see "Hammer" in the results
    And I should see "Wrench" in the results
    And I should see "Apple" in the results
    And I should see "Banana" in the results
    And I should see "Car Wax" in the results
    And the "ID" column should contain the ID of "Hat"
    And the "Name" column should contain "Hat"
    And the "Description" column should contain "A red fedora"
    And the "Available" column should contain "True"
    And the "Category" column should contain "CLOTHS"
    And the "Price" column should contain "59.95"

Scenario: Search Products by Name
    When I visit the "Home Page"
    And I set the "Name" to "Hammer"
    And I press the "Search" button
    Then I should see "Hammer" in the results
    And I should not see "Hat" in the results
    And the "Name" column should contain "Hammer"
    And the "ID" column should contain the ID of "Hammer"

Scenario: Search Products by Category
    When I visit the "Home Page"
    And I select "FOOD" in the "Category" dropdown
    And I press the "Search" button
    Then I should see "Big Mac" in the results
    And I should see "Apple" in the results
    And I should see "Banana" in the results
    And I should not see "Hat" in the results
    And the "Category" column should contain "FOOD"

Scenario: Search Products by Availability
    When I visit the "Home Page"
    And I select "False" in the "Available" dropdown
    And I press the "Search" button
    Then I should see "Shoes" in the results
    And I should not see "Hat" in the results
    And the "Available" column should contain "False"

Scenario: Search Products by Name and Category
    When I visit the "Home Page"
    And I set the "Name" to "Hammer"
    And I select "TOOLS" in the "Category" dropdown
    And I press the "Search" button
    Then I should see "Hammer" in the results
    And I should not see "Wrench" in the results
    And the "Name" column should contain "Hammer"
    And the "Category" column should contain "TOOLS"
