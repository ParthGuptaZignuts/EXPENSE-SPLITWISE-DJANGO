from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class UserDetails(models.Model):
    ROLE_CHOICES = [
        ('GROUPADMIN', 'Group Admin'),
        ('SUPERADMIN', 'Super Admin'),
        ('USER', 'User'),
    ]

    user         = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=10, null=True, blank=True)
    role         = models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

    def __str__(self):
        return f'{self.user.username} - {self.role}'
