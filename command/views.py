from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from logs.mqtt_service import publish_command


class SendCommandAPIView(APIView):

    def post(self, request):
        try:
            publish_command(request.data)

            return Response(
                {"status": "Command sent"}
            )

        except ValueError as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as error:
            return Response(
                {"error": str(error)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )