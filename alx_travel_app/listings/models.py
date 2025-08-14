from django.db import models
from django.utils import timezone

class Listing(models.Model):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.title

class Booking(models.Model):
    user_email = models.EmailField()
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Booking #{self.pk} - {self.user_email}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Completed", "Completed"),
        ("Failed", "Failed"),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payments")
    transaction_id = models.CharField(max_length=255, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Pending")
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.booking} - {self.status} - {self.transaction_id}"
