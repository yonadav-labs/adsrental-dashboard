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

       

    
    Scenario: New lead avalible
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        Then I should see "Available" in column "Status"




    Scenario: Lead get RaspberryPi
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click checkbox with name "_selected_action"
        And I type "Mark Facebook account as qualified" in field "action"
        And I click button "Go"
        Then I should see "Qualified" in column "Status"



 Scenario: Lead moves from available to qualified
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click link "Vlad Emelianov"
        And I type "Jon" in field "lead_accounts-1-username"
        And I type "Jonsan" in field "lead_accounts-1-password"
        And I type "Google" in field "lead_accounts-1-account_type"
        And I type "Jack" in field "lead_accounts-2-username"
        And I type "Jackson" in field "lead_accounts-2-password"
        And I type "Amazon" in field "lead_accounts-2-account_type"
        And I click button "Save"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        Then I should see "Google Jon (Available)" in column "Accounts"
        And I should see "Amazon Jack (Available" in column "Accounts"


    Scenario: Ban Google account
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban google account" in field "action"
       And I click button "Go" 
       And I type "bad conection" in field "note"
       And I click button "Ban" 
       Then I should see text on page "is banned"


     

    Scenario: Ban amazon account
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban amazon account" in field "action"
       And I click button "Go" 
       And I type "bad conection" in field "note"
       And I click button "Ban" 
       Then I should see text on page "is banned"


    Scenario: Ban facebook account
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban facebook account" in field "action"
       And I click button "Go" 
       And I type "bad conection" in field "note"
       And I click button "Ban" 
       Then I should see text on page "is banned"
     



    Scenario: Ban lead
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban lead" in field "action"
       And I click button "Go" 
       Then I should see text on page "is banned"


     Scenario: New lead Banned
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        Then I should see "Banned" in column "Status"