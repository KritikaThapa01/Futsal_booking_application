from django.db import models

class Court(models.Model):
    COURT_TYPES = [
        ('premium', 'Premium'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
    ]
    
    name = models.CharField(max_length=100)
    court_type = models.CharField(max_length=20, choices=COURT_TYPES)
    price_per_hour = models.DecimalField(max_digits=8, decimal_places=2)
    
    def __str__(self):
        return f"{self.get_court_type_display()} Court ({self.name})" 