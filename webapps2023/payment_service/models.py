from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    CURRENCY_CHOICES = (
        ('GBP', 'British Pound'),
        ('USD', 'US Dollar'),
        ('EUR', 'Euro'),
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='GBP')
    # previous_balance = models.DecimalField(max_digits=10, decimal_places=2, default=1000)

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('P', 'Pending'),
        ('A', 'Accepted'),
        ('R', 'Rejected'),
    )
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_transactions')
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CustomUser.CURRENCY_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_request = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)