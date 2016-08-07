import json
import requests


class PAHappnUser:
    """Class representing a Happn user"""

    def __init__(self, happn_user: dict):
        """Create a user object, based on the response from a successful get call for the user"""
        self.id = happn_user.get('id')
        self.facebook_id = happn_user.get('fb_id')
        self.twitter_id = happn_user.get('twitter_id')

        self.first_name = happn_user.get('first_name')
        self.display_name = happn_user.get('display_name')
        self.nickname = happn_user.get('nickname')
        self.gender = happn_user.get('gender')
        self.work = happn_user.get('workplace')

