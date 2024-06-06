from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from common.models.base_models import BaseModel


class Hotel(BaseModel):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    stars = models.PositiveSmallIntegerField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()

    def __str__(self):
        return self.name


class Staff(BaseModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='staff_hotel')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    hire_date = models.DateField()

    # Django automatically creates indexes for primary keys and foreign keys
    # class Meta:
    #     indexes = [
    #         models.Index(fields=['hotel']),
    #     ]

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Guest(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class RoomType(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255, null=True, blank=True)
    price_per_night = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    capacity = models.PositiveSmallIntegerField()

    def __str__(self):
        return self.name


class Room(BaseModel):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'

    STATUS_CHOICES = [
        (AVAILABLE, 'Available'),
        (OCCUPIED, 'Occupied'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_hotel')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='room_type')
    room_number = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=AVAILABLE)

    def __str__(self):
        return self.room_number


class Booking(BaseModel):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='booking_guest')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booking_room')
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return f'{self.guest} booking for {self.room}'

    def clean(self):
        super().clean()

        if self.check_out_date <= self.check_in_date:
            raise ValidationError(
                {'check_out_date': _('Check-out date must be after check-in date.')}
            )

        if self.check_in_date < timezone.now().date():
            raise ValidationError({'check_in_date': _('Check-in date cannot be in the past.')})

    def save(self, *args, **kwargs):
        # Validate the model
        self.full_clean()
        super().save(*args, **kwargs)


class Payment(BaseModel):
    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_CREDIT_CARD = 'credit_card'
    PAYMENT_METHOD_DEBIT_CARD = 'debit_card'
    PAYMENT_METHOD_BANK_TRANSFER = 'bank_transfer'

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, 'Cash'),
        (PAYMENT_METHOD_CREDIT_CARD, 'Credit Card'),
        (PAYMENT_METHOD_DEBIT_CARD, 'Debit Card'),
        (PAYMENT_METHOD_BANK_TRANSFER, 'Bank Transfer'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_booking')
    amount = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_CASH
    )
