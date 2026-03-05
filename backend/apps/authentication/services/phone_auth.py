from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class PhoneLoginView(APIView):
    def post(self, request):
        return Response({"detail": "Phone login placeholder"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    def post(self, request):
        return Response({"detail": "Verify OTP placeholder"}, status=status.HTTP_200_OK)
