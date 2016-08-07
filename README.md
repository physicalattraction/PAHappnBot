# PAHappnBot
Do something with the Happn API.

## General use

## Secrets file

You need to store your Facebook ID and a Facebook authentication token in the file secrets.json.
This file secrets.json is not in the Git repository, since it contains your personal information.
To create it, perform the following:

- Copy secrets_template.json to secrets.json
- Visit the following URL to find your Facebook ID, and fill it in the secrets file:
http://findmyfbid.com/
- Visit the following URL to find your Facebook auth token, and fill it in the secrets file:
https://www.facebook.com/dialog/oauth?client_id=464891386855067&redirect_uri=https://www.facebook.com/connect/login_success.html&scope=basic_info,email,public_profile,user_about_me,user_activities,user_birthday,user_education_history,user_friends,user_interests,user_likes,user_location,user_photos,user_relationship_details&response_type=token
- Copy the token quickly from the address bar in your browser, before it disappears.