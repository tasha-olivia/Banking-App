from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomerRegistrationForm, ManagerRegistrationForm, TransferForm, LoanRequestForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Account, Transaction, LoanRequest
from django.shortcuts import render
from django.contrib import messages
from django.db import transaction as db_transaction
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse

def root_redirect(request):
    return redirect('login')

def home(request):
    return render(request, 'core/home.html')
import random
from .models import Account

def generate_account_number():
    while True:
        number = str(random.randint(1000000000, 9999999999))  # 10-digit number
        if not Account.objects.filter(account_number=number).exists():
            return number

def register_customer_view(request):
    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create an account for the new user, pending approval
            account_number = generate_account_number()
            Account.objects.create(
                user=user,
                account_number=account_number,
                balance=5000,
                is_approved=False
)
            return redirect('login')
    else:
        form = CustomerRegistrationForm()
    return render(request, 'core/register_customer.html', {'form': form})

def register_manager_view(request):
    if request.method == 'POST':
        form = ManagerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('manager_dashboard')
    else:
        form = ManagerRegistrationForm()
    return render(request, 'core/register_manager.html', {'form': form})

# def login_view(request):
#     if request.method == 'POST':
#         form = AuthenticationForm(request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request, user)
#             # Redirect based on role
#             if user.is_manager:
#                 return redirect('manager_dashboard')
#             else:
#                 return redirect('customer_dashboard')
#     else:
#         form = AuthenticationForm()
#     return render(request, 'core/login.html', {'form': form})

def customer_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if (hasattr(user, 'is_customer') and user.is_customer) or user.is_superuser:
                # Check if the account is approved
                try:
                    account = Account.objects.get(user=user)
                    if not account.is_approved:
                        messages.error(request, "Your account has not been approved by the admin yet.")
                        return render(request, 'core/customer_login.html', {'form': form})
                except Account.DoesNotExist:
                    messages.error(request, "No account found for this user.")
                    return render(request, 'core/customer_login.html', {'form': form})
                login(request, user)
                return redirect('customer_dashboard')
            else:
                messages.error(request, "You are not registered as a customer.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/customer_login.html', {'form': form})
    
def manager_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            if user.is_manager:
                login(request, user)
                return redirect('manager_dashboard')
            else:
                messages.error(request, "You are not registered as a manager.")
        else:
            messages.error(request, "Invalid credentials.")
    else:
        form = AuthenticationForm()
    return render(request, 'core/manager_login.html', {'form': form})


@login_required
def customer_dashboard(request):
    account = Account.objects.get(user=request.user)
    if account.is_frozen:
        return HttpResponse("Your account is currently frozen. Contact support.")
    sent = Transaction.objects.filter(sender=account)
    received = Transaction.objects.filter(receiver=account)
    transactions = (sent | received).order_by('-timestamp')[:10]
    return render(request, 'core/customer_dashboard.html', {
        'account': account,
        'transactions': transactions,
    })

@login_required
def transfer_funds(request):
    account = Account.objects.get(user=request.user)

  # 🔐 Add approval and freeze checks
    if not account.is_approved:
        return HttpResponse("Your account is not approved yet. Please wait for manager approval.")
    if account.is_frozen:
        return HttpResponse("Your account is currently frozen. Contact support.")
    
    if request.method == 'POST':
        form = TransferForm(request.POST)
        if form.is_valid():
            receiver = form.cleaned_data['to_account']
            amount = form.cleaned_data['amount']

            if account == receiver:
                form.add_error('to_account', "You can't transfer to your own account.")
            elif account.balance < amount:
                form.add_error('amount', "Insufficient funds.")
            else:
                # Perform atomic transaction
                with db_transaction.atomic():
                    account.balance -= amount
                    receiver.balance += amount
                    account.save()
                    receiver.save()

                    Transaction.objects.create(sender=account, receiver=receiver, amount=amount)
                messages.success(request, "Transfer successful.")
                return render(request, 'core/transfer_success.html', {'amount': amount})

    else:
        form = TransferForm()

    return render(request, 'core/transfer_funds.html', {'form': form, 'balance': account.balance})

# @login_required
# def manager_dashboard(request):
#     if not request.user.is_manager:
#         return redirect('home')
#     pending_accounts = Account.objects.filter(is_approved=False)
#     customers = Account.objects.filter(is_approved=True)
#     return render(request, 'core/manager_dashboard.html', {
#         'pending_accounts': pending_accounts,
#         'customers': customers,
#     })
@login_required
def manager_dashboard(request):
    if not request.user.is_manager:
        return redirect('home')
    pending_accounts = Account.objects.filter(is_approved=False)
    customers = Account.objects.filter(is_approved=True)
    approved_accounts = Account.objects.filter(is_approved=True)  # Add this line
    loans = LoanRequest.objects.all().order_by('-created_at')
    transactions = Transaction.objects.all().order_by('-timestamp')[:50]  # Last 50 transactions for audit
    return render(request, 'core/manager_dashboard.html', {
        'pending_accounts': pending_accounts,
        'customers': customers,
        'approved_accounts': approved_accounts,  # Pass to template
        'loans': loans,
        'transactions': transactions,
    })

@login_required
def approve_account(request, id):
    if not request.user.is_manager:
        return redirect('home')
    acct = get_object_or_404(Account, id=id)
    acct.is_approved = True
    acct.save()
    return redirect('manager_dashboard')

@login_required
def deny_account(request, id):
    if not request.user.is_manager:
        return redirect('home')
    acct = get_object_or_404(Account, id=id)
    acct.is_approved = False  # Mark as not approved/denied
    acct.save()
    return redirect('manager_dashboard')

@login_required
def freeze_account(request, id):
    acct = get_object_or_404(Account, id=id)
    acct.is_frozen = True
    acct.save()
    return redirect('manager_dashboard')

@login_required
def unfreeze_account(request, id):
    acct = get_object_or_404(Account, id=id)
    acct.is_frozen = False
    acct.save()
    return redirect('manager_dashboard')


# @login_required
# def request_loan(request):
#     acct = Account.objects.get(user=request.user)
#     if acct.is_frozen:
#         return HttpResponse("Your account is currently frozen. You cannot request a loan.")
#     if request.method == 'POST':
#         form = LoanRequestForm(request.POST)
#         if form.is_valid():
#             loan = form.save(commit=False)
#             loan.account = acct
#             loan.save()
#             return HttpResponse("Loan request submitted.")
#     else:
#         form = LoanRequestForm()
#     return render(request, 'core/request_loan.html', {'form': form})

@login_required
def request_loan(request):
    account = Account.objects.get(user=request.user)
    if account.is_frozen:
        return render(request, 'core/request_loan.html', {'error': 'Your account is frozen. You cannot request a loan.'})
    if request.method == 'POST':
        form = LoanRequestForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            loan.account = account
            loan.save()
            return render(request, 'core/request_loan.html', {'form': LoanRequestForm(), 'success': 'Loan request submitted!'})
    else:
        form = LoanRequestForm()
    return render(request, 'core/request_loan.html', {'form': form})

@login_required
def manage_loans(request):
    if not request.user.is_manager:
        return redirect('home')
    loans = LoanRequest.objects.all().order_by('-created_at')
    return render(request, 'core/manage_loans.html', {'loans': loans})

@login_required
def approve_loan(request, id):
    loan = get_object_or_404(LoanRequest, id=id)
    loan.is_approved = True
    loan.account.balance += loan.amount
    loan.account.save()
    loan.save()
    return redirect('manager_dashboard')

@login_required
def deny_loan(request, id):
    loan = get_object_or_404(LoanRequest, id=id)
    loan.is_approved = False
    loan.save()
    return redirect('manager_dashboard')

