@wip
Feature: Lead lifespan
    In order to check if all links in Admin Dashboard are working
    As an Admin
    I want to login and click all links in Admin Dashboard

    Scenario: Links check
        Given I am using initial database
        And I sign up as a lead
        When I type "1234567890" in field "phone"
        And I type "https://www.facebook.com" in field "facebook_profile_url"
        And I type "olvida@mail.ru" in field "fb_email"
        And I type "65656565" in field "fb_secret"
        And I type "150" in field "fb_friends"
        And I type "street" in field "street"
        And I type "67" in field "apartment"
        And I type "sfms" in field "city"
        And I type "Oregon" in field "state"
        And I type "5348489" in field "postal_code"
        And I upload file "file.png" in field "photo_id"
        And I upload file "file.png" in field "extra_photo_id"
        And I click radio with name "apply_type" and value "splashtop"
        And I click checkbox with name "accept"
        And I click button "Click Here to Apply"
        And I type "9944455" in field "splashtop_id"
        And I click button "Submit"
        Then I should see text on page "Thank you! Our agent will contact you shortly"

    Scenario: Qualify lead
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click checkbox with name "_selected_action"
        And I type "Mark Facebook account as qualified" in field "action"
        And I click button "Go"
        Then I should see "Qualified" in column "Status"

    Scenario: Mark RaspberryPi as tested
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click link "RP00001000"
        And I click link "RP00001000"
        And I type "2019-05-10" in field "first_tested_0"
        And I type "11:22:28" in field "first_tested_1"
        And I click button "Save"
        Then I should see enabled check mark in column "Tested"
        







