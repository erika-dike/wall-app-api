from rest_framework import serializers

from accounts.serializers import ProfileDetailSerializer
from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    owner = ProfileDetailSerializer(read_only=True)
    num_loves = serializers.IntegerField(read_only=True)
    in_love = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ('date_created', 'content', 'owner', 'num_loves', 'in_love')
