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
    https://www.facebook.com/login.php?skip_api_login=1&api_key=247294518656661&signed_next=1&next=https%3A%2F%2Fwww.facebook.com%2Fv2.6%2Fdialog%2Foauth%3Fredirect_uri%3Dhttps%253A%252F%252Fwww.happn.fr%26scope%3Demail%252Cpublic_profile%26response_type%3Dtoken%26client_id%3D247294518656661%26ret%3Dlogin%26logger_id%3Da49034f5-0e29-43f0-8c1f-ad09a41153de&cancel_url=https%3A%2F%2Fwww.happn.fr%2F%3Ferror%3Daccess_denied%26error_code%3D200%26error_description%3DPermissions%2Berror%26error_reason%3Duser_denied%23_%3D_&display=page&locale=nl_NL&logger_id=a49034f5-0e29-43f0-8c1f-ad09a41153de