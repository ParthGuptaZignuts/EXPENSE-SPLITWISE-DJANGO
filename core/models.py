from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
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
    deleted_at   = models.DateTimeField(null=True, blank=True)
    is_deleted   = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.role}'

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.is_deleted = False
        self.save()
