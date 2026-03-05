from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class Enable2FAView(APIView):
    def post(self, request):
        return Response({"detail": "Enable 2FA placeholder"}, status=status.HTTP_200_OK)


class Verify2FAView(APIView):
    def post(self, request):
        return Response({"detail": "Verify 2FA placeholder"}, status=status.HTTP_200_OK)
