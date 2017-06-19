from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import Love, Post
from core.pagination import StandardResultsSetPagination
from core.serializers import PostSerializer


class PostList(generics.ListCreateAPIView):
    """Handles the creation and Listing of all Posts on the database"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        """Returns queryset in order of date last modified by default
        However, if the query string says top posts, order posts by number
        of loves
        """
        search_str = self.request.query_params.get('q', '')
        limit = self.request.query_params.get('limit', 10)
        private = self.request.query_params.get('private', False)

        qs = Post.get_queryset(self.request.user.id)
        if private:
            qs = Post.filter_others_post(qs, self.request.user)
        if search_str.lower() == 'top':
            qs = Post.order_queryset_by_num_loves(qs, int(limit))

        return qs

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    """Handles fetching, updating and deleting a single user"""
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        """Returns queryset in order of date last modified by default"""
        qs = Post.get_queryset(self.request.user.id)
        return qs


class LoveView(APIView):
    """Handles users loving or unloving a post"""
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, post_id, format=None):
        if Post.objects.filter(id=post_id).exists():
            Love.create_love(request.user, post_id)
            num_loves = Love.get_num_post_loves(post_id)
            response_payload = self._get_success_response_payload(
                int(post_id), num_loves, True
            )
            return Response(response_payload, status=status.HTTP_201_CREATED)
        return Response(
            self._get_failure_response_payload,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, post_id, format=None):
        if Post.objects.filter(id=post_id).exists():
            Love.delete_love(request.user, post_id)
            num_loves = Love.get_num_post_loves(post_id)
            response_payload = self._get_success_response_payload(
                int(post_id), num_loves, False
            )
            return Response(
                response_payload, status=status.HTTP_200_OK)
        return Response(
            self._get_failure_response_payload,
            status=status.HTTP_400_BAD_REQUEST)

    @staticmethod
    def _get_success_response_payload(post_id, num_loves, in_love):
        """Returns a dictionary of success response"""
        return {
            'post_id': post_id,
            'num_loves': num_loves,
            'in_love': in_love
        }

    @staticmethod
    def _get_failure_response_payload():
        """Returns failure response payload"""
        return {'error': 'Invalid Post ID'}
