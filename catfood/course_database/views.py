from rest_framework.response import Response
from rest_framework.views import APIView


class AliveView(APIView):

    def get(self, request, format=None):
        response = 'alive'
        content = {
            "response": f"{response}"
        }
        return Response(content)
