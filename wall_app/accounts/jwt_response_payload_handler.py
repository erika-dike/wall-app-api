from accounts.serializers import ProfileDetailSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    """
    Override to add profile user's profile to returned payload
    """
    return {
        'token': token,
        'profile': ProfileDetailSerializer(
            user.profile, context={'request': request}).data
    }
