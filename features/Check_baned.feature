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


   Scenario: Account became Qualified
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Faceboook account as Qualified" in field "action"
       And I click button "Go"
       And I click checkbox with name "_selected_action"
       And I type "Mark Google account as Qualified" in field "action"
       And I click button "Go"
       And I click checkbox with name "_selected_action"
       And I type "Mark Amazon account as Qualified" in field "action"
       And I click button "Go"
       Then I should see "Qualified" in column "Status"
       And I should see "Google Jon (Qualified)" in column "Accounts"
       And I should see "Amazon Jack (Qualified)" in column "Accounts"
       And I should see "Facebook olvida@mail.ru (Qualified)" in column "Accounts"


  Scenario: Re-Qualification should not change lead status (Faceboook account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Faceboook account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Facebook lead olvida@mail.ru order already exists"


  Scenario: Re-Qualification should not change lead status (Google account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Google account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Google lead Jon order already exists:"


   Scenario: Re-Qualification should not change lead status (Amazon account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Amazon account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Lead Amazon lead Jack order already exists"
       And  I should see "Qualified" in column "Status"


   Scenario: Status check after ban and unban (Faceboook account)part 1
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
       Then I should see "Facebook olvida@mail.ru (Banned)" in column "Accounts"
      

   Scenario: Status check after ban and unban (Faceboook account)part 2
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Unban facebook account" in field "action"
       And I click button "Go"
       Then I should see "Facebook olvida@mail.ru (Qualified), " in column "Accounts"


   Scenario: Status check after ban and unban (Amazon account)part 1
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
       Then I should see "Amazon Jack (Banned)" in column "Accounts"
      

    Scenario: Status check after ban and unban (Amazon account)part 2
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Unban amazon account" in field "action"
       And I click button "Go"
       Then I should see "Amazon Jack (Qualified)" in column "Accounts"

       
    Scenario: Check. Re-qualification does not changenithing (Facebook account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Faceboook account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Facebook lead olvida@mail.ru order already exists"
       And I should see "Facebook olvida@mail.ru (Qualified), " in column "Accounts"


    Scenario: Check. Re-qualification does not changenithing  (Google account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Google account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Google lead Jon order already exists"
       And I should see "Google Jon (Qualified)" in column "Accounts"


    Scenario: Check. Re-qualification does not changenithing  (Amazon account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Mark Amazon account as Qualified" in field "action"
       And I click button "Go"
       Then I should see text on page "Lead Amazon lead Jack order already exists: None."
       And  I should see "Amazon Jack (Qualified)" in column "Accounts"
       And  I should see "Qualified" in column "Status"


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


    Scenario: Send ping from RaspberryPi
         Given I go to url "/log/?rpid=RP00001000&p=&version=2.0.8&attempt=1&hostname=123.123.123.123"
         Then I should see text on page "result"
         And I should see text on page "true"
         And I should see text on page "source"
         And I should see text on page "ping"


    Scenario: Check. Re-qualification does not changenithing  (Amazon account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       Then I should see "In-Progress" in column "Status"
       And I should see "Facebook olvida@mail.ru (In-Progress), " in column "Accounts"
       And I should see "Google Jon (In-Progress)" in column "Accounts"
       And I should see "Amazon Jack (In-Progress)" in column "Accounts"


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
       Then I should see "Banned" in column "Status"


    Scenario: Checking that status after unban uncanged (Google account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Unban google account" in field "action"
       And I click button "Go"
       Then I should see "Google Jon (In-Progress)" in column "Accounts"


    Scenario: Checking that status after unban uncanged (Amazon account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Unban amazon account" in field "action"
       And I click button "Go" 
       Then I should see "Amazon Jack (In-Progress)" in column "Accounts"


    Scenario: Checking that status after unban uncanged (Facebook account)
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Unban facebook account" in field "action"
       And I click button "Go" 
       Then I should see "Facebook olvida@mail.ru (In-Progress), " in column "Accounts"
       And I should see "In-Progress" in column "Status"
     

  Scenario: Checking - In the presence of an active account the Lead can not banned
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban lead" in field "action"
       And I click button "Go"
       Then I should see text on page "has active accounts, ban them first"


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
     

    Scenario: Cheacking - Lead can be banned if all accounts have status - banned 
       Given I am logged in as an Admin
       And I am on main Admin Dashboard page
       When I click link "Leads"
       And I type "RP00001000" in field "q"
       And I click button "Search"
       And I click checkbox with name "_selected_action"
       And I type "Ban lead" in field "action"
       And I click button "Go" 
       Then I should see "Banned" in column "Status"

