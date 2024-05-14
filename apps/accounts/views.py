from rest_framework.viewsets import ModelViewSet
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.models import Group, Permission
from .models import User
from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    UserTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from .permissions import UserPermissions


class GroupViewSet(ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionViewSet(ModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer


class UserTokenObtainPairView(TokenObtainPairView):
    serializer_class = UserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Retrieve the user from the serializer
            user = serializer.user

            # Add custom claims to the response data
            response.data['user_id'] = user.id
            response.data['email'] = user.email

        return response


class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegisterSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.all().order_by('-updated_at')
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]
    # required_permissions = ['auth.view_user', 'auth.edit_user']


class UserMeView(RetrieveUpdateAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
