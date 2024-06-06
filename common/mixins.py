from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from .exceptions import NotFoundError


class SoftDeleteMixin:
    def get_queryset(self):
        if self.action in ['restore', 'hard_delete']:
            return self.queryset.model.all_objects.all()
        return self.queryset.model.objects.all()

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        obj = queryset.get(pk=self.kwargs["pk"])
        self.check_object_permissions(self.request, obj)
        return obj

    def _get_instance_or_404(self, pk):
        try:
            instance = self.queryset.model.all_objects.get(pk=pk)
            self.check_object_permissions(self.request, instance)
            return instance
        except self.queryset.model.DoesNotExist:
            raise NotFoundError(f"{self.queryset.model.__name__} not found")

    @action(detail=False, methods=['get'], url_path='soft-delete')
    def soft_delete(self, request):
        deleted_instances = self.queryset.model.deleted_objects.all()

        # Paginate the queryset of deleted instances
        page = self.paginate_queryset(deleted_instances)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(deleted_instances, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='restore')
    def restore(self, request, pk=None):
        instance = self._get_instance_or_404(pk)
        if instance.is_deleted:
            instance.restore()
            return Response(
                {'status': f'{self.queryset.model.__name__} restored'}, status=status.HTTP_200_OK
            )
        return Response(
            {'status': f'{self.queryset.model.__name__} is not deleted'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    @action(detail=True, methods=['delete'], url_path='hard-delete')
    def hard_delete(self, request, pk=None):
        instance = self._get_instance_or_404(pk)
        instance.hard_delete()
        return Response(
            {'status': f'{self.queryset.model.__name__} permanently deleted'},
            status=status.HTTP_204_NO_CONTENT,
        )
