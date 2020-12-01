from django.shortcuts import render

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view

@api_view(['POST'])
def post_register(request):
  realname = request.get('realname')
  content = {
    "realname" : f"{realname}"
  }
  return Response(content)

@api_view(['PATCH'])#different with APIdoc
def patch_change_password(request):
  #TODO： User Authentication
  content = {
    'isSuccess' : true,
    data : {
      'message' : 'password changed successfully'
    }
  }
  return Response(content)

@api_view(['POST'])
def post_accounts(request):
  #TODO： User Authentication
  content = {
    'isSuccess' : true,
    data : {
      'message' : 'accounts appended successfully'
    }
  }
  return Response(content)

class DefaultView(APIView):

  def get(self, request, format=None):
    return Response('this is the default page')

class LoginView(APIView):

  def get(self, request, format=None):
    return Response('login with token')

  def post(self, request, format=None):
    user_id = request.get('user_id')
    password_digest = request.get('password_digest')
    # read from db
    isSuccess = true
    content = {
      'isSuccess' : f"{isSuccess}",
      data : {
        'user_id' : f"{user_id}"
      }
    }
    return Response(content)

class AccountView(APIView):

  def get(self, request, user_id, format=None):#different with APIdoc
    return Response('the info of user ' + user_id)

  def patch(self, request, user_id, format=None):
    #TODO： User Authentication
    #different with APIdoc
    isSuccess = true
    content = {
      'isSuccess' : f"{isSuccess}",
      data : {
        'user_id' : f"{user_id}"
      }
    }
    return Response(content)
