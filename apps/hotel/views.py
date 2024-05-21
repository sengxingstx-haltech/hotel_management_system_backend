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


class PaymentViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
