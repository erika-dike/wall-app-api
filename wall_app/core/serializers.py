from rest_framework import serializers

from accounts.serializers import ProfileDetailSerializer
from core.models import Post


class PostSerializer(serializers.ModelSerializer):
    owner = ProfileDetailSerializer(read_only=True)

    class Meta:
        model = Post
        fields = ('date_created', 'content', 'owner')


class LoveSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()

    def validate_post_id(self, value):
        """Check if a post with this id exists"""
        if not Post.objects.filter(id=value).exists():
            raise serializers.ValidationError("Invalid Post ID")
        return value
