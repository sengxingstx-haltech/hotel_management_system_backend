from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import status
from datetime import datetime
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
from .permissions import HotelPermissions, StaffPermissions


class HotelViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    permission_classes = [HotelPermissions]


class StaffViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [StaffPermissions]


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

    @action(detail=False, methods=['get'], url_path='report', permission_classes=[IsAuthenticated])
    def report(self, request):
        """
        Generate a report of bookings.
        """
        # Customize the reporting logic as needed
        # For example, filter by date range, group by room type, etc.
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        bookings = self.queryset

        if not start_date or not end_date:
            raise ValidationError("Both 'start_date' and 'end_date' are required.")

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError("Invalid date format. Use 'YYYY-MM-DD'.")

        if start_date > end_date:
            raise ValidationError("'start_date' must be before 'end_date'.")

        bookings = self.queryset.filter(check_in_date__gte=start_date, check_out_date__lte=end_date)

        report_data = bookings.values(
            'guest__first_name',
            'guest__last_name',
            'room__room_number',
            'check_in_date',
            'check_out_date',
            'total_price',
        )

        # Calculate the total sum of all total_price
        total_sum = bookings.aggregate(total_sum=Sum('total_price'))['total_sum']

        # Count the number of bookings within the specified range
        booking_count = bookings.count()

        return Response(
            {
                'report': report_data,
                'total_bookings': booking_count,
                'total_sum': total_sum,
            },
            status=status.HTTP_200_OK,
        )


class PaymentViewSet(BaseModelViewSet, SoftDeleteMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
