import re

from django.test import TestCase

from factories.factories import ProfileFactory, UserFactory

from accounts.tokens import account_activation_token


class AccountActivationTokenTestSuite(TestCase):
    def test_returns_string(self):
        profile = ProfileFactory()
        token = account_activation_token.make_token(profile.user)
        self.assertEqual(type(token), unicode)

    def test_string_returned_passes_regex_expected_in_url(self):
        usernames = [
            'janey', 'johnny', 'randalph', 'tuvwe', 'minime', 'titwa',
            'chalmanders', 'gupta', 'walter', 'abu_nakud' 'wonder_woman'
        ]

        for username in usernames:
            user = UserFactory(username=username)
            profile = ProfileFactory(user=user)
            token = account_activation_token.make_token(profile.user)

            pattern = re.compile('[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}')
            self.assertTrue(pattern.match(token))
