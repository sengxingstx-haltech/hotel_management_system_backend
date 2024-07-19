from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveUpdateAPIView,
)
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.models import Group, Permission
from django.http import Http404
from django.contrib.auth import logout as django_logout

from .models import User
from .serializers import (
    GroupSerializer,
    PermissionSerializer,
    UserTokenObtainPairSerializer,
    UserRegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
from common.viewsets.base_viewsets import BaseModelViewSet
from .permissions import UserPermissions


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


class UserMeView(RetrieveUpdateAPIView):
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(BaseModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [UserPermissions]

    def get_queryset(self):
        # For normal operations, use the default queryset
        if self.action in ['restore', 'hard_delete']:
            return User.all_objects.all()
        return User.objects.all()

    def get_object(self):
        # Override to fetch from all_objects
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def _get_user_or_404(self, pk):
        try:
            user = User.all_objects.get(pk=pk)
            self.check_object_permissions(self.request, user)
            return user
        except User.DoesNotExist:
            raise Http404("User not found")

    @action(detail=False, methods=['get'], url_path='soft-delete')
    def soft_delete(self, request):
        deleted_users = User.deleted_objects.all()

        # Paginate the queryset of deleted instances
        page = self.paginate_queryset(deleted_users)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(deleted_users, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        user = self._get_user_or_404(pk)

        if user.is_deleted:
            user.restore()
            return Response({'status': 'user restored'}, status=status.HTTP_200_OK)
        return Response({'status': 'user is not deleted'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='hard-delete')
    def hard_delete(self, request, pk=None):
        user = self._get_user_or_404(pk)

        user.hard_delete()
        return Response({'status': 'user permanently deleted'}, status=status.HTTP_204_NO_CONTENT)


class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        # For session-based authentication
        django_logout(request)

        # For token-based authentication
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response(status=status.HTTP_204_NO_CONTENT)


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Change password
            self.object.set_password(serializer.data['new_password'])
            self.object.save()
            return Response({'status': 'password set'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(GenericAPIView):
    serializer_class = PasswordResetSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password reset email sent'}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'password reset successful'}, status=status.HTTP_200_OK)


class GroupViewSet(BaseModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PermissionViewSet(BaseModelViewSet):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
