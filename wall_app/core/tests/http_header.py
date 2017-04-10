from rest_framework.test import APITestCase
from rest_framework_jwt.settings import api_settings

from factories.factories import ProfileFactory


class APIHeaderAuthorization(APITestCase):
    """Base class used to attach header to all request on setup."""

    def setUp(self):
        """Include an appropriate `Authorization:` header on all requests"""
        self.profile = ProfileFactory()
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(self.profile.user)
        token = jwt_encode_handler(payload)
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token)
