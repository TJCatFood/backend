from rest_framework import authentication
from rest_framework import exceptions
from django.contrib import auth
from .models import User
from django.core.exceptions import ObjectDoesNotExist


class CatfoodAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        if request.session.get("login"):
            user_id = request.session.get('user_id')
            try:
                user = User.objects.get(user_id=user_id)
                # In case users change their passwords
                if request.session.get("password") != user.password:
                    raise exceptions.AuthenticationFailed('未登录或cookie失效/被浏览器禁用')
            except(ObjectDoesNotExist):
                raise exceptions.AuthenticationFailed('用户不存在')
        else:
            raise exceptions.AuthenticationFailed('未登录或cookie失效/被浏览器禁用')

        return (user, None)
