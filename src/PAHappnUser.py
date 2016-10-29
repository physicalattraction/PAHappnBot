import json
import requests


class PAHappnUser:
    """Class representing a Happn user"""

    def __init__(self, happn_user: dict):
        """Create a user object, based on the response from a successful get call for the user"""

        for field in self.fields():
            setattr(self, field, happn_user.get(field))

        # Sometimes, fb_id is called facebook_id in Happn's APIs
        if 'facebook_id' in happn_user:
            self.fb_id = happn_user.get('facebook_id')

        # If available, also store the number of crossings. This is only available from the
        # crossings API, not from the get user API, therefore it is not included in fields()
        self.nb_times = happn_user.get('nb_times')

    @staticmethod
    def fields():
        return [
            'id', 'fb_id', 'twitter_id',
            'first_name', 'display_name', 'nickname',
            'age', 'gender',
            'school', 'job', 'workplace',
            'has_charmed_me'
        ]

    def __str__(self):
        return '{} (http://www.facebook.com/{})'.format(self.display_name, self.fb_id)
