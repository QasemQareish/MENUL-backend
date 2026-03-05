from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.restaurants.models import Table
from .services import create_session_if_not_exists


class CustomerLoginAPIView(APIView):
    permission_classes = []

    def post(self, request):
        table_number = request.data.get("table_number")
        password = request.data.get("session_password")

        try:
            table = Table.objects.get(number=table_number)
        except Table.DoesNotExist:
            return Response({"error": "الطاولة غير موجودة"}, status=404)

        if table.current_session_password != password:
            return Response({"error": "كلمة المرور غير صحيحة"}, status=400)

        session = create_session_if_not_exists(table)

        return Response({
            "session_id": session.id,
            "session_password": session.session_password
        })
