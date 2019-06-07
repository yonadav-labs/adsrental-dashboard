
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

     Scenario: Lead moves from available to qualified
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click link "Vlad Emelianov"
        And I type "Neblad" in field "lead_accounts-1-username"
        And I type "Zuzu" in field "lead_accounts-1-password"
        And I type "Google" in field "lead_accounts-1-account_type"
        And I type "Nevlad" in field "lead_accounts-2-username"
        And I type "Xuxu" in field "lead_accounts-2-password"
        And I type "Amazon" in field "lead_accounts-2-account_type"
        And I click button "Save"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        Then I should see "Google Neblad (Available)" in column "Accounts"
        And I should see "Amazon Nevlad (Available" in column "Accounts"


      Scenario: Mark accounts as Qualified
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click checkbox with name "_selected_action"
        And I type "Mark Google account as qualified" in field "action"
        And I click button "Go" 
        And I click checkbox with name "_selected_action"
        And I type "Mark Amazon account as qualified" in field "action"
        And I click button "Go" 
        Then I should see "Facebook olvida@mail.ru (Qualified)" in column "Accounts"

      Scenario: RaspberryPi reset cache
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Raspberry pis"
        And I type "RP00001000" in field "q"
        And I click button "Search"
        And I click checkbox with name "_selected_action"
        And I type "reset_cache" in field "action"
        And I click button "Go" 
        Then I should see text on page "Cache reset successful for RP00001000."



      Scenario: Check bundler leads
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Bundlers"
        And I click checkbox with name "_selected_action"
        Then I should see "2" in column "Leads"


     Scenario: Send ping from RaspberryPi
         Given I go to url "/log/?rpid=RP00001000&p=&version=2.0.8&attempt=1&hostname=123.123.123.123"
         Then I should see text on page "result"
         And I should see text on page "true"
         And I should see text on page "source"
         And I should see text on page "ping"



     Scenario: Check accounts status
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Leads"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        Then I should see "Google Neblad (In-Progress)" in column "Accounts"
        And I should see "Amazon Nevlad (In-Progress)" in column "Accounts"
        And I should see "Facebook olvida@mail.ru (In-Progress)" in column "Accounts"

    Scenario: Check bundler active
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Bundlers"
        And I type "600" in field "q"
        And I click button "Search"
        Then I should see enabled check mark in column "Is active"

    Scenario: Check bundler payments
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Bundlers"
        And I type "600" in field "q"
        And I click button "Search"
        And I click link "Payments"
        Then I should see text on page "Bundler Jason Taylor"
        And I should see text on page "Total pay for Facebook accounts"
        And I should see text on page "Total"

    Scenario: Check RaspberryPi log
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Raspberry pis"
        And I type "RP00001000" in field "q"
        And I click button "Search"
        Then I should see enabled check mark in column "Online"

    
    Scenario: Generate daily lead timestamps
        Given I go to url "/cron/lead_history/?now=true"
        Then I should see text on page "true"


    Scenario: Check lead 
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Lead Timestamps"
        And I type "volshebnyii@gmail.com" in field "q"
        And I click button "Search"
        And I click the first row in table
        And I type "20" in field "checks_online"
        And I click button "Save"
        Then I should see enabled check mark in column "Active"
        And I should see enabled check mark in column "Online"
        And I see hint "Facebook account in-progress"
        And I see hint "Google account in-progress"
        And I see hint "Amazon account in-progress"
        And I see hint "Total: $1.3333"

    Scenario: Generate lead histories month
        Given I go to url "/cron/lead_history/?aggregate=true"
        Then I should see text on page "true"



    Scenario: Check lead histories month
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Lead Histories Month"
        And I type "RP00001000" in field "q"
        And I click button "Search"
        Then I should see enabled check mark in column "Move to next month"
        And I should see "1" in column "Days online"
        And I should see "0" in column "Days offline"
        And I should see "0" in column "Days wrong password"
        And I should see "0" in column "Days sec checkpoint"
        And I should see "$1.33" in column "Payment"
        And I should see "$1.33" in column "Amount Total"


    Scenario: Debug aggregate
        Given I am logged in as an Admin
        And I am on main Admin Dashboard page
        When I click link "Lead Histories Month"
        And I type "RP00001000" in field "q"
        And I click button "Search"
        And I click checkbox with name "_selected_action"
        And I type "DEBUG Aggregate" in field "action"
        And I click button "Go" 


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
















        







