from rest_framework import views,permissions,response

class TestLogin(views.APIView):
    permission_classes =  permissions.IsAuthenticated

    def get(request):
        return response.Response()