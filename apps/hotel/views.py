from django.db import transaction
from django.utils import timezone
from rest_framework.response import Response
from rest_framework import status
from .models import Hotel, Staff, Guest, RoomType, Room, Booking, Payment
from .serializers import (
    HotelSerializer,
    StaffSerializer,
    GuestSerializer,
    RoomTypeSerializer,
    RoomSerializer,
    BookingSerializer,
    PaymentSerializer,
)
from common.viewsets.base_viewsets import BaseModelViewSet
from common.mixins import SoftDeleteMixin


class HotelViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer


class StaffViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer


class GuestViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer


class RoomTypeViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer


class RoomViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class BookingViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        payment_method = request.data.get('payment_method', Payment.PAYMENT_METHOD_CASH)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            self.perform_create(serializer)
            instance = serializer.instance

            # Create payment upon successful booking
            Payment.objects.create(
                booking=instance,
                amount=instance.total_price,
                payment_date=timezone.now(),
                payment_method=payment_method,  # Use provided payment method or default to cash
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class PaymentViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
