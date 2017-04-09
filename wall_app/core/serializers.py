from rest_framework import serializers

from accounts.serializers import ProfileDetailSerializer
from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    owner = ProfileDetailSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('date_created', 'content', 'owner')
