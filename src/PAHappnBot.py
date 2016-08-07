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

from PAHappnUser import PAHappnUser

import json
import os
import requests


class PAHappnBot:

    def __init__(self):
        self.secrets = self._read_secrets_file()
        self.root_url = 'https://api.happn.fr/'

        self.oauth_token = None
        self.me = None
        self.log_in()

    def run_happn_bot(self):
        pass

    def log_in(self):
        """Use the Facebook oAuth token to retrieve a Happn oAuth token"""
        url = '{root_url}connect/oauth/token/'.format(root_url=self.root_url)
        # Set a known user agent, otherwise the Happn API thinks you are a bot
        # and refuses to cooperate.
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0'
        }
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
            happn_id = response.get('user_id')
            self.oauth_token = response.get('access_token')
            self.me = self.get_happn_user(happn_id)

            is_new = response.get('is_new')
            if is_new:
                welcome_message = 'Welcome'
            else:
                welcome_message = 'Welcome back'
            print("Logged in as Happn user with ID {happn_id}.".format(happn_id=self.me.id))
            print("{welcome_message}, {display_name}!".format(
                welcome_message=welcome_message, display_name=self.me.display_name))
        else:
            msg = 'Obtaining oAuth token fails. Status code: {}'.format(r.status_code)
            raise ConnectionError(msg)

    def get_recommendations(self):
        pass

    def get_happn_user(self, happn_id: str) -> PAHappnUser:
        """Given a Happn user ID, return a Happn user object"""
        url = '{root_url}api/users/{happn_id}/'.format(root_url=self.root_url, happn_id=happn_id)
        headers = {
            'Authorization': 'OAuth="{}"'.format(self.oauth_token),
            'Content-Type': 'application/json',
            'User-Agent': 'Happn/19.1.0 AndroidSDK/19'
        }
        r = requests.get(url, headers=headers)

        if r.status_code == requests.codes.ok:
            response = json.loads(r.text)
            user_info_dict = response.get('data')
            user = PAHappnUser(user_info_dict)
            return user
        else:
            msg = 'Obtaining Happn user {} fails. Status code: {}'.format(happn_id, r.status_code)
            raise ConnectionError(msg)

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
