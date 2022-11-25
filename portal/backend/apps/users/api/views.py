from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserDisplaySerializer


class CurrentUserAPIView(APIView):

    # Get current user from every request
    def get(self, request):
        serializer = UserDisplaySerializer(request.user)
        return Response(serializer.data)
