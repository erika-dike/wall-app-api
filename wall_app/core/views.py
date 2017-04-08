from rest_framework import generics, permissions

from core.models import Message
from core.serializers import MessageSerializer


class MessageList(generics.ListCreateAPIView):
    """Handles the creation and Listing of all Messages on the database"""
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user.profile)
