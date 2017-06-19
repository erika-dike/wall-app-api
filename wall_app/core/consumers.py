import json

from django.conf import settings
from channels import Group


def connect_post(message):
    """
    When the user opens a WebSocket to a live post stream, adds them to the
    group for that stream so they receive new post notification

    The notifications are actually sent in the Post model on save.
    """
    message.reply_channel.send({'accept': True})
    # Each different client has a different 'reply_channel', which is how you
    # send information back to them. We can add all the different reply
    # channels to a single Group, and then when we send to the group,
    # they'll all get the same message
    Group(settings.GLOBAL_CHANNEL_NAME).add(message.reply_channel)


def disconnect_post(message):
    """
    Removes the user from the global group when they disconnect.

    Channels will auto-cleanup eventually, but it can take a while, and having
    old entries cluttering up the group will reduce performance.
    """
    Group(settings.GLOBAL_CHANNEL_NAME).discard(message.reply_channel)


def send_post_to_clients(post):
    """
    This consumer is in charge of sending newly created or modified posts
    to all clients in the global group

    This function is called from the core/models.py
    I didn't just send it from the models to avoid circular import errors
    when importing PostSerializer.
    """
    from .serializers import PostSerializer
    serialized_post = PostSerializer(post)
    payload = {
        'type': 'post_update',
        'data': serialized_post.data
    }

    # Encode and send that message to the general channel
    Group(settings.GLOBAL_CHANNEL_NAME).send({
        'text': json.dumps(payload)
    })


def send_post_delete_command_to_clients(post_id):
    """
    This consumer is in charge of informing clients of post removal

    This function is called from the core/models.py
    """
    payload = {
        'type': 'post_delete',
        'data': post_id,
    }

    # Encode and send that message to the general channel
    Group(settings.GLOBAL_CHANNEL_NAME).send({'text': json.dumps(payload)})


def send_love_status_to_clients(data):
    """
    This consumer is in charge of sending love status changes to users
    connected to the global channel

    Now, I think it just makes sense that all uses of the channel be located
    in one place
    """
    # Encode and send that message to the general channel
    payload = {
        'type': 'love_update',
        'data': data
    }
    Group(settings.GLOBAL_CHANNEL_NAME).send({'text': json.dumps(payload)})
