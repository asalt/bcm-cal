from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project_number = models.IntegerField()
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"Project {self.project_number}: {self.name}"


class Booking(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("not_available", "Not Available"),
        ("booked_by_user", "Booked by User"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time_slot = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, null=True, blank=True
    )
    reservation_expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("date", "time_slot")  # Prevent double booking

    def __str__(self):
        return f"{self.user.username} - {self.date} at {self.time_slot}"

    def __str__(self):
        return f"{self.user.username} - {self.date} {self.time_slot}"


class Availability(models.Model):
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="availabilities"
    )
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"Availability for {self.booking}"
