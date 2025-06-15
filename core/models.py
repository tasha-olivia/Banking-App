from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
    is_customer = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)

class Account(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True)
    balance = models.DecimalField(max_digits=12, decimal_places=2)

 # 🔐 Manager feature flags:
    is_approved = models.BooleanField(default=False)  # For manager approval
    is_frozen = models.BooleanField(default=False)    # For freezing accounts
    

    def __str__(self):
        return f"{self.user.username} - {self.account_number}"

class Transaction(models.Model):
    sender = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='sent_transactions')
    receiver = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='received_transactions')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.account_number} → {self.receiver.account_number} : {self.amount}"

# class LoanRequest(models.Model):
#     account = models.ForeignKey(Account, on_delete=models.CASCADE)
#     amount = models.DecimalField(max_digits=10, decimal_places=2)
#     reason = models.TextField()
#     is_approved = models.BooleanField(null=True)  # None = pending
#     created_at = models.DateTimeField(auto_now_add=True)



class LoanRequest(models.Model):
    account = models.ForeignKey('Account', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reason = models.CharField(max_length=255)
    is_approved = models.BooleanField(null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
