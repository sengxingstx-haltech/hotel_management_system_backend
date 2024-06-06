from celery import shared_task
from django.utils import timezone
from apps.hotel.models import Room, Booking


@shared_task
def update_room_status():
    today = timezone.now().date()
    expired_bookings = Booking.objects.filter(check_out_date__lt=today, room__status=Room.OCCUPIED)

    for booking in expired_bookings:
        room = booking.room
        room.status = Room.AVAILABLE
        room.save()
