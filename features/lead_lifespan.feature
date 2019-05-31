@wip
Feature: Lead lifespan
    In order to check if all links in Admin Dashboard are working
    As an Admin
    I want to login and click all links in Admin Dashboard

    Scenario: Links check
        Given I am using initial database
        And I sign up as a lead
        When I type "1234567890" in field phone
        And I type "https://www.facebook.com" in field facebook_profile_url
        And I type "olvida@mail.ru" in field fb_email
        And I type "65656565" in field fb_secret
        And I type "150" in field fb_friends
        And I type "street" in field street
        And I type "67" in field apartment
        And I type "sfms" in field city
        And I type "Oregon" in field state
        And I type "5348489" in field postal_code
        And I upload file "file.png" in field photo_id
        And I upload file "file.png" in field extra_photo_id
        And I click radio with name "apply_type" and value "splashtop"
        And I click checkbox with name "accept"
        And I click button "Click Here to Apply"
        And I type "9944455" in field splashtop_id
        And I click button "Submit"
        Then I should see text on page "Thank you! Our agent will contact you shortly"
        


#    Scenario: RaspberryPi is tested
#       Given I am logged in as an Admin
#       And I am on main Admin Dashboard page
#       When I click link "Leads"
#       And I should see text on page "Select lead to change"
#       And I I click checkbox with name "_selected_action"
#       And I type 'Mark Facebook account as qualified' in field action
#       And I click button "Go"
#       And I see disabled check mark "False"
#       And I click link "RP999"
#       And I click checkbox with name "_selected_action"
#       And I click link "RP999"
#      And I should see text on page "Change raspberry pi"






