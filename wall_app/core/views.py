from rest_framework import generics, permissions

from core.models import Post
from core.pagination import StandardResultsSetPagination
from core.serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
    """Handles the creation and Listing of all Posts on the database"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    """Handles fetching, updating and deleting a single user"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)
