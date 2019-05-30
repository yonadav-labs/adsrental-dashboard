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

    Scenario: Pi.conf check
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I click link "pi.conf"
        And I click link "Stats"
        Then I should see text on page "Lead"
         
   Scenario: History check
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I click link "History"
        Then I should see text on page "Select lead change to change"

   Scenario: Leads check
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I click link "Checks"
       Then I should see text on page "Select Lead History Month to change"

   Scenario: Cost check
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       When I click link "Cost"
       Then I should see text on page "Monthly payments"