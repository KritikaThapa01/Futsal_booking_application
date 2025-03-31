from django.db import models
from django.contrib.auth.models import User
from .court import Court

class CourtBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    court = models.ForeignKey(Court, on_delete=models.CASCADE)
    booking_date = models.DateField()
    start_time = models.TimeField()
    duration = models.IntegerField(default=1)  # in hours
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.court.name} - {self.booking_date} {self.start_time}" 