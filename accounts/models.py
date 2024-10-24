from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user           = models.ForeignKey(User, on_delete=models.CASCADE, related_name='accounts')
    account_type   = models.CharField(max_length=20,default="WALLET")
    account_value  = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username}'s Account"
