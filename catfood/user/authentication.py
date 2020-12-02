from rest_framework import authentication
from rest_framework import exceptions
from django.contrib import auth

class ExampleAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        username = request.POST.get('username')
        if not username:
            raise exceptions.AuthenticationFailed('Username Required')
        try:
            user = auth.get_user_model().objects.get(username=username)
        except:
            raise exceptions.AuthenticationFailed('No such user')
        return (user, None)