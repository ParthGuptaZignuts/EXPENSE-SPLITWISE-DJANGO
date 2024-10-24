from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Account(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_type   = models.CharField(max_length=20, default="WALLET")
    account_value  = models.IntegerField(default=0)
    deleted_at     = models.DateTimeField(null=True, blank=True)
    is_deleted     = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Account"

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()
    
    def restore(self):
        self.deleted_at = None
        self.is_deleted = False
        self.save()
