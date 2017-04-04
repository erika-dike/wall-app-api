from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from accounts.serializers import RegisterSerializer
from accounts.models import SiteUser


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permisssions = [AllowAny]
    queryset = SiteUser.objects.all()
