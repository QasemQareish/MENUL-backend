from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class GoogleLoginView(APIView):
    def post(self, request):
        return Response({"detail": "Google login placeholder"}, status=status.HTTP_200_OK)
