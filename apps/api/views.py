from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


class APIRootView(APIView):
    def get(self, request, *args, **kwargs):
        data = {
            'auth': {
                'signin': reverse('api:auth-signin', request=request),
                'register': reverse('api:auth-register', request=request),
                'logout': reverse('api:logout', request=request),
                'change-password': reverse('api:change-password', request=request),
                'reset-password': reverse('api:reset-password', request=request),
                'reset-password-confirm': reverse(
                    'api:reset-password-confirm', request=request, format=None
                ),
                'refresh_token': reverse('api:token_refresh', request=request),
                'auth-me': reverse('api:auth-me', request=request, format=None),
            },
            'users': reverse('api:user-list', request=request, format=None),
            'groups': reverse('api:group-list', request=request, format=None),
            'permissions': reverse('api:permission-list', request=request, format=None),
            'hotels': reverse('api:hotel-list', request=request, format=None),
            'staff': reverse('api:staff-list', request=request, format=None),
            'guests': reverse('api:guest-list', request=request, format=None),
            'room-types': reverse('api:roomtype-list', request=request, format=None),
            'rooms': reverse('api:room-list', request=request, format=None),
            'bookings': reverse('api:booking-list', request=request, format=None),
            'payments': reverse('api:payment-list', request=request, format=None),
        }

        return Response(data)
