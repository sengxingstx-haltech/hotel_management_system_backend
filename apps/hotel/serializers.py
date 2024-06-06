from django.utils import timezone
from rest_framework import serializers
from .models import Hotel, Staff, Guest, RoomType, Room, Booking, Payment


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'


class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'


class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

    def validate(self, data):
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        room = data.get('room')

        if room.status == Room.OCCUPIED:
            raise serializers.ValidationError(
                {'room': "The room is currently occupied and cannot be booked."}
            )

        if check_in_date and check_in_date < timezone.now().date():
            raise serializers.ValidationError(
                {'check_in_date': 'Check-in date cannot be in the past.'}
            )

        if check_out_date and check_in_date and check_out_date <= check_in_date:
            raise serializers.ValidationError(
                {'check_out_date': 'Check-out date must be after check-in date.'}
            )

        return data


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'
