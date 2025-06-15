from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Account, LoanRequest, Transaction

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_customer = True
        if commit:
            user.save()
        return user

class ManagerRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_manager = True
        if commit:
            user.save()
        return user

class TransferForm(forms.Form):
    to_account = forms.CharField(label="Recipient Account Number")
    amount = forms.DecimalField(min_value=0.01)

    def clean_to_account(self):
        acct_number = self.cleaned_data['to_account']
        try:
            return Account.objects.get(account_number=acct_number)
        except Account.DoesNotExist:
            raise forms.ValidationError("Account not found.")

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['amount', 'reason']
