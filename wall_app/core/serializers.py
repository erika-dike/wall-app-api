from rest_framework import serializers

from accounts.serializers import ProfileDetailSerializer
from core.models import Message


class MessageSerializer(serializers.ModelSerializer):
    owner = ProfileDetailSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('date_created', 'content', 'owner')
