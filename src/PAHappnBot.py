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
import operator
from collections import OrderedDict
from pprint import pprint

from PAHappnUser import PAHappnUser

import json
import os
import requests


class PAHappnBot:
    ACTION_NO_ACTION = 0
    ACTION_LIKE = 1
    ACTION_DISLIKE = 2

    def __init__(self):
        self.secrets = self._read_secrets_file()
        self.liked_users = self._read_liked_users_file()
        self.root_url = 'https://api.happn.fr/'
        self.headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Happn/19.1.0 AndroidSDK/19'
        }

        self.oauth_token = None
        self.me = None
        self.log_in()

    def run_happn_bot(self):
        crossings = self.get_crossings(limit=250)
        nr_liked = nr_disliked = nr_no_action = 0
        for index, (happn_id, nb_times) in enumerate(crossings.items()):
            action = self.determine_action(happn_id, nb_times, index + 1)
            if action == self.ACTION_LIKE:
                self.like_user(happn_id)
                nr_liked +=1
            elif action == self.ACTION_DISLIKE:
                self.dislike_user(happn_id)
                nr_disliked += 1
            elif action == self.ACTION_NO_ACTION:
                nr_no_action += 1
        print('Processed {} possible dates'.format(len(crossings)))
        print('Summary: {} liked, {} disliked, {} no action'.format(nr_liked, nr_disliked, nr_no_action))

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
            self.headers['Authorization'] = 'OAuth="{}"'.format(self.oauth_token)
            self.me = self.get_happn_user(happn_id)

            is_new = response.get('is_new', True)
            if is_new:
                welcome_message = 'Welcome'
            else:
                welcome_message = 'Welcome back'
            print("Logged in as Happn user with ID {happn_id}.".format(happn_id=self.me.id))
            print("{welcome_message}, {display_name}!\n".format(
                welcome_message=welcome_message, display_name=self.me.display_name))
        else:
            msg = 'Obtaining oAuth token fails. Status code: {}'.format(r.status_code)
            raise ConnectionError(msg)

    def get_crossings(self, limit=None) -> OrderedDict:
        """
        Return all crossings as a list of Happn ids
        """
        if limit is None:
            print('Retrieving crossings...')
        else:
            print('Retrieving {} crossings...'.format(limit))

        url = '{}/api/users/{}/crossings/'.format(self.root_url, self.me.id)

        fields = ['nb_times', 'notifier']
        params = {
            'fields': ','.join(fields)
        }

        if limit:
            params['limit'] = limit

        response = requests.get(url, headers=self.headers, params=params)
        if response.status_code != 200:
            msg = 'ERROR. Failed to fetch crossings. Status code {}\n'.format(response.status_code)
            msg += 'URL: {}'.format(response.url)
            raise ConnectionError(msg)

        response = response.json().get('data', [])

        result = OrderedDict()
        for crossing in response:
            nb_times = crossing['nb_times']
            notifier = crossing['notifier']
            happn_id = notifier['id']

            # For known users, update the number of times in the liked_users file
            # This data is only available from the crossings API
            if happn_id in self.liked_users:
                if self.liked_users[happn_id].nb_times != nb_times:
                    self.liked_users[happn_id].nb_times = nb_times
                    self._update_liked_users_file()

            result[happn_id] = nb_times

        print('Retrieved {} crossings'.format(len(result)))

        return result

    def determine_action(self, happn_id: str, nb_times: int = 0, index=None, output=True):
        index_string = ''
        if index is not None:
            index_string = '{} - '.format(index)

        if nb_times == 1:
            if output:
                print('{}NO ACTION: User {} has only 1 crossing'.format(index_string, happn_id))
            return self.ACTION_NO_ACTION
        if happn_id in self.liked_users:
            user = self.liked_users[happn_id]
            if output:
                print('{}NO ACTION: User {} has already been liked'.format(index_string, user))
            return self.ACTION_NO_ACTION

        user = self.get_happn_user(happn_id)
        if user.school is None or len(user.school) < 2:
            if output:
                print('{}DISLIKE: User {} has no school defined'.format(index_string, user))
            if happn_id in self.liked_users:
                # It could be that the user was already liked before.
                # We remove the user from the liked_users list
                del self.liked_users[happn_id]
                self._update_liked_users_file()
            return self.ACTION_DISLIKE
        else:
            if output:
                print('{}LIKE: User {}'.format(index_string, user))
            user.nb_times = nb_times
            self.liked_users[happn_id] = user
            self._update_liked_users_file()
            return self.ACTION_LIKE

    def like_user(self, happn_id: str):
        """
        Like another user with the given user_id

        :param happn_id: Happn user id as a string
        """
        url = '{}/api/users/{}/accepted/{}'.format(self.root_url, self.me.id, happn_id)
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:
            msg = 'ERROR. Failed to like another user. Status code {}'.format(response.status_code)
            raise ConnectionError(msg)

    def dislike_user(self, happn_id: str):
        """
        Dislike another user with the given user_id

        :param happn_id: Happn user id as a string
        """
        url = '{}/api/users/{}/rejected/{}'.format(self.root_url, self.me.id, happn_id)
        response = requests.post(url, headers=self.headers)
        if response.status_code != 200:
            msg = 'ERROR. Failed to dislike another user. Status code {}'.format(
                response.status_code)
            raise ConnectionError(msg)

    def get_happn_user(self, happn_id: str) -> PAHappnUser:
        """Given a Happn user ID, return a Happn user object"""
        url = '{root_url}api/users/{happn_id}/'.format(root_url=self.root_url, happn_id=happn_id)
        headers = {
            'Authorization': 'OAuth="{}"'.format(self.oauth_token),
            'Content-Type': 'application/json',
            'User-Agent': 'Happn/19.1.0 AndroidSDK/19'
        }
        params = {'fields': ','.join(PAHappnUser.fields())}
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == requests.codes.ok:
            response = json.loads(r.text)
            user_info_dict = response.get('data')
            user = PAHappnUser(user_info_dict)
            return user
        else:
            msg = 'Obtaining Happn user {} fails. Status code: {}'.format(happn_id, r.status_code)
            raise ConnectionError(msg)

    def analyze_liked_users(self):
        fields_to_analyze = ['school', 'age', 'nb_times', 'display_name', 'gender']
        for field in fields_to_analyze:
            field_count = {}
            for user in self.liked_users.values():
                field_value = getattr(user, field)
                if field_value in field_count:
                    field_count[field_value] += 1
                else:
                    field_count[field_value] = 1
            print()
            print('** {} **'.format(field))
            pprint(sorted(field_count.items(), key=operator.itemgetter(1)))

    def _read_secrets_file(self):
        secrets_file = self._get_secrets_file_name()
        if os.path.isfile(secrets_file):
            with open(secrets_file, 'r') as f:
                secrets = json.load(f)
            return secrets
        return {}

    def _read_liked_users_file(self) -> dict:
        liked_users_file = self._get_liked_users_file_name()
        if not os.path.isfile(liked_users_file):
            return OrderedDict()

        with open(liked_users_file, 'r') as f:
            liked_users_list = json.load(f)
        print('You have liked {} users so far with PAHappnBot'.format(len(liked_users_list)))

        liked_users_dict = OrderedDict()
        for liked_user in liked_users_list:
            happn_id = liked_user['id']
            happn_user = PAHappnUser(liked_user)
            liked_users_dict[happn_id] = happn_user

        return liked_users_dict

    def _update_liked_users_file(self):
        liked_users_file = self._get_liked_users_file_name()
        with open(liked_users_file, 'w') as f:
            liked_users = [user.__dict__ for user in self.liked_users.values()]
            liked_users = sorted(liked_users, key=lambda k: k['id'])
            json.dump(liked_users, f, indent=4)

    @staticmethod
    def get_facebook_auth_token_url():
        url = 'https://www.facebook.com/v2.6/dialog/oauth'
        params = {
            'api_key': '247294518656661',  # Happn's App ID
            'redirect_uri': 'https://www.happn.fr',  # Happn's whitelisted redirect URI
            'response_type': 'token',
            'scope': 'email,public_profile'
        }
        response = requests.get(url, params)
        return response.url

    @staticmethod
    def _get_json_dir():
        current_dir = os.path.dirname(__file__)
        json_dir = os.path.join(current_dir, '..', 'json')
        return json_dir

    @staticmethod
    def _get_secrets_file_name():
        secrets_file = 'secrets.json'
        return os.path.join(PAHappnBot._get_json_dir(), secrets_file)

    @staticmethod
    def _get_liked_users_file_name():
        liked_users_file = 'liked_users.json'
        return os.path.join(PAHappnBot._get_json_dir(), liked_users_file)


if __name__ == '__main__':
    print('Visit this URL to retrieve your Facebook auth token:\n{}\n'.format(
        PAHappnBot.get_facebook_auth_token_url()))

    happn_bot = PAHappnBot()
    happn_bot.run_happn_bot()
    # happn_bot.analyze_liked_users()
