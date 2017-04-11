from rest_framework import serializers

from accounts.serializers import UserDetailSerializer
from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserDetailSerializer(read_only=True)
    num_loves = serializers.IntegerField(read_only=True)
    in_love = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = ('date_created', 'content', 'author', 'num_loves', 'in_love')
