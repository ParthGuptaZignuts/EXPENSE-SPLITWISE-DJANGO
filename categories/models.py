from django.db import models
from django.contrib.auth.models import User

class Categories(models.Model):
    CATEGORY_TYPES = (
        ('EXPENSE', 'Expense'),
        ('INCOME', 'Income'),
    )

    EXPENSE_FIELDS = ('FOOD', 'BILLS', 'TRANSPORT', 'SHOPPING')
    INCOME_FIELDS = ('SALARY', 'REFUNDS')

    user          = models.ForeignKey(User, on_delete=models.CASCADE)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPES)
    category_name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('user', 'category_name')
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"{self.user.username} - {self.category_type} - {self.category_name}"
