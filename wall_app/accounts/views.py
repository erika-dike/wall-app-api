from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import sendgrid
from sendgrid.helpers.mail import Email, Content, Mail

from accounts.models import Profile
from accounts.serializers import RegisterSerializer
from accounts.tokens import account_activation_token


class RegistrationView(CreateAPIView):
    serializer_class = RegisterSerializer
    permisssions = [AllowAny]
    queryset = Profile.objects.all()

    def post(self, request, format=None, *args, **kwargs):
        # response = super(RegisterView, self).post(request, *args, **kwargs)
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        self.send_mail(request, profile)  # should run asynchronously
        response = serializer.data
        response.update({
            'msg': 'Please confirm your email address to complete registration'
        })
        return Response(response, status=status.HTTP_201_CREATED)

    def send_mail(self, request, profile):
        current_site = get_current_site(request)
        subject = 'Confirm your account on Wallie'
        message = render_to_string('accounts/account_activation_email.html', {
            'first_name': profile.user.first_name,
            'domain': current_site.domain,
            'uid': urlsafe_base64_encode(force_bytes(profile.user.pk)),
            'token': account_activation_token.make_token(profile.user),
        })
        sg = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)
        from_email = Email("admin@wallie.com")
        to_email = Email(profile.user.email)
        content = Content("text/html", message)
        mail = Mail(from_email, subject, to_email, content)
        response = sg.client.mail.send.post(request_body=mail.get())


class ActivationView(View):
    """Handles user account activation"""
    def get(self, request, uidb64, token):
        frontend_app_url = 'http://localhost:3000/'
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        import ipdb; ipdb.set_trace()
        if (user is not None and
                account_activation_token.check_token(user, token)):
            user.is_active = True
            user.profile.email_confirmed = True
            user.save()
            user.profile.save()
            status = 'success'
        else:
            status = 'failed'
        return redirect('{url}?status={status}'.format(
            url=frontend_app_url, status=status))
