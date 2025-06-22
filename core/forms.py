from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Account, LoanRequest, Transaction
from django.utils.html import strip_tags

class CustomerRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_username(self):
        username = self.cleaned_data['username']
        # Prevent spaces and strip HTML tags
        username = strip_tags(username)
        if " " in username:
            raise forms.ValidationError("Username cannot contain spaces.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        email = strip_tags(email)
        return email

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
    
    def clean_username(self):
        username = self.cleaned_data['username']
        username = strip_tags(username)
        if " " in username:
            raise forms.ValidationError("Username cannot contain spaces.")
        return username

    def clean_email(self):
        email = self.cleaned_data['email']
        email = strip_tags(email)
        return email

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
        acct_number = strip_tags(self.cleaned_data['to_account'])
        try:
            return Account.objects.get(account_number=acct_number)
        except Account.DoesNotExist:
            raise forms.ValidationError("Account not found.")

class LoanRequestForm(forms.ModelForm):
    class Meta:
        model = LoanRequest
        fields = ['amount', 'reason']

    def clean_reason(self):
        reason = self.cleaned_data['reason']
        reason = strip_tags(reason)
        if len(reason) < 5:
            raise forms.ValidationError("Please provide a more detailed reason.")
        return reason