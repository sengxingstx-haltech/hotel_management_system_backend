from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class APIRootView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'auth': {
                'signin': reverse('accounts:auth-signin', request=request),
                'register': reverse('accounts:auth-register', request=request),
                # 'logout': reverse('accounts:logout', request=request, format=format),
                # 'password_change': reverse('accounts:password_change', request=request, format=format),
                'refresh_token': reverse('accounts:token_refresh', request=request),
                'auth-me': reverse('accounts:auth-me', request=request, format=None),
            },
            'users': reverse('accounts:user-list', request=request, format=None),
            'groups': reverse('accounts:group-list', request=request, format=None),
            'permissions': reverse('accounts:permission-list', request=request, format=None),
        }

        return Response(data)
