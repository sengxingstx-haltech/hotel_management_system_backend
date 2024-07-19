from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated


class BaseModelViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
