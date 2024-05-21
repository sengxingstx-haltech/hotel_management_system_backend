from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Room


@receiver(post_save, sender=Booking)
def update_room_status_on_booking(sender, instance, created, **kwargs):
    if created:
        # Calculate the total price
        nights = (instance.check_out_date - instance.check_in_date).days
        room_type = instance.room.room_type
        instance.total_price = nights * room_type.price_per_night
        instance.save()

        # Set the room status to 'occupied'
        room = instance.room
        room.status = Room.OCCUPIED
        room.save()


@receiver(post_delete, sender=Booking)
def update_room_status_on_checkout(sender, instance, **kwargs):
    room = instance.room
    room.status = Room.AVAILABLE
    room.save()
