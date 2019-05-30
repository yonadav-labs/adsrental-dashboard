Feature: Admin UI
    In order to check if all links in Admin Dashboard are working
    As an Admin
    I want to login and click all links in Admin Dashboard

    Scenario: Links check
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I click link "Proxy tunnel"
        Then I should see text on page "RP999 proxy tunnel info"
