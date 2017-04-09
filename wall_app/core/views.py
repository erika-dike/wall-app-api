from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Love, Post
from core.pagination import StandardResultsSetPagination
from core.serializers import LoveSerializer, PostSerializer


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


class LoveCreate(APIView):
    """Handles users loving a post"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, post_id, format=None):
        if Post.objects.filter(id=post_id).exists():
            Love.create_love(request.user.profile, post_id)
            numLoves = Love.get_num_post_loves(post_id)
            response_payload = {
                'num_loves': numLoves,
                'in_love': True
            }
            return Response(response_payload, status=status.HTTP_201_CREATED)
        return Response(
            {'error': 'Invalid Post ID'},
            status=status.HTTP_400_BAD_REQUEST
        )


class LoveDelete(APIView):
    """Handles users unloving a post"""
    permission_classes = (permissions.IsAuthenticated,)

    def delete(self, request, post_id, format=None):
        if Post.objects.filter(id=post_id).exists():
            Love.delete_love(request.user.profile, post_id)
            numLoves = Love.get_num_post_loves(post_id)
            response_payload = {
                'num_loves': numLoves,
                'in_love': False
            }
            return Response(
                response_payload, status=status.HTTP_200_OK)
        return Response(
            {'error': 'Invalid Post ID'},
            status=status.HTTP_400_BAD_REQUEST)
