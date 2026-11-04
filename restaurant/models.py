from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Menu(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.00'))])
    inventory = models.PositiveSmallIntegerField(default=0)
    class Meta:
        ordering = ['id']
        constraints = [models.CheckConstraint(condition=models.Q(price__gte=0), name='menu_price_nonnegative')]
    def __str__(self):
        return f'{self.title} : {self.price}'

class Booking(models.Model):
    name = models.CharField(max_length=255)
    no_of_guests = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(20)])
    booking_date = models.DateTimeField()
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    class Meta:
        ordering = ['booking_date', 'id']
        constraints = [models.CheckConstraint(condition=models.Q(no_of_guests__gte=1, no_of_guests__lte=20), name='booking_guest_range')]
    def __str__(self):
        return f'{self.name} - {self.booking_date:%Y-%m-%d %H:%M}'
