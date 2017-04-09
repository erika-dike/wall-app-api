from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings

from accounts.models import Profile
from accounts.tests.test_api_views import BaseTestCase


class APIHeaderAuthorization(BaseTestCase):
    """Base class used to attach header to all request on setup."""

    def setUp(self):
        """Include an appropriate `Authorization:` header on all requests"""
        user = User.objects.create_user(**self.user_details)
        self.profile = Profile.objects.create(
            user=user, **self.profile_details
        )
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
