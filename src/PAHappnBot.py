"""
PAHappnBot: automatically find and like Happn profiles
Copyright (C) 2016  physicalattraction

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import os
import requests


class PAHappnBot:

    def __init__(self):
        self.secrets = self._read_secrets_file()
        self.root_url = 'https://api.happn.fr/'
        # Set a known user agent, otherwise the Happn API thinks you are a bot
        # and refuses to cooperate.
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded',
                        'User-Agent': 'Mozilla/5.0'}
        self.oauth_token = self.get_oauth_token()

    def run_happn_bot(self):
        self.get_recommendations()

    def get_oauth_token(self):
        """Use the Facebook oAuth token to retrieve a Happn oAuth token"""
        url = '{root_url}connect/oauth/token/'.format(root_url=self.root_url)
        headers = self.headers
        payload = {
            'client_id': self.secrets.get('CLIENT_ID'),
            'client_secret': self.secrets.get('CLIENT_SECRET'),
            'grant_type': 'assertion',
            'assertion_type': 'facebook_access_token',
            'assertion': self.secrets.get('FACEBOOK_AUTH_TOKEN'),
            'scope': 'mobile_app'
        }
        r = requests.post(url, headers=headers, data=payload)

        if r.status_code == requests.codes.ok:
            response = json.loads(r.text)
            user_id = response.get('user_id')
            print("Logged in as Happn user with ID {}".format(user_id))
            oauth_token = response.get('access_token')
            return oauth_token
        else:
            msg = 'Obtaining oAuth token fails. Status code: {}'.format(r.status_code)
            raise ConnectionError(msg)

    def get_recommendations(self):
        pass

    def _read_secrets_file(self):
        secrets_file = self._get_secrets_file_name()
        with open(secrets_file) as f:
            secrets = json.loads(f.read())
        return secrets

    @staticmethod
    def _get_json_dir():
        current_dir = os.path.dirname(__file__)
        json_dir = os.path.join(current_dir, '..', 'json')
        return json_dir

    def _get_secrets_file_name(self):
        secrets_file = 'secrets.json'
        return os.path.join(self._get_json_dir(), secrets_file)

if __name__ == '__main__':
    happn_bot = PAHappnBot()
    happn_bot.run_happn_bot()
