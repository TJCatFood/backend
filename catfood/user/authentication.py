from rest_framework import authentication
from rest_framework import exceptions
from django.contrib import auth
from .models import User

class CatfoodAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.session.get("login"):
            user_id = request.session.get('user_id')
            try:
                user = User.objects.get(user_id=user_id)
            except:
                raise exceptions.AuthenticationFailed('用户不存在')
        else:
            raise exceptions.AuthenticationFailed('未登录或cookie被禁用')
        return (user, None)