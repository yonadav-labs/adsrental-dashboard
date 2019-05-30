Feature: Admin login
    In order to check if all links in Admin Dashboard are working
    As an Admin
    I want to login and click all links in Admin Dashboard

    Scenario: Login with correct credentials
        Given I am logged in as an Admin
        Then Admin Dashboard should be shown

    Scenario: Login with wrong credentials
        Given I am logged in as an Admin with wrong password
        Then I am on url "/admin/login/"
        And I should see text on page "Please enter the correct email and password"
