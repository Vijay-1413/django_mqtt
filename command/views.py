from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .mqtt_service import publish_command


class SendCommandAPIView(APIView):

    def post(self, request):

        data = request.data

        publish_command(data)

        return Response(
            {
                "status": "Command sent",
                "data": data
            },
            status=status.HTTP_200_OK
        )