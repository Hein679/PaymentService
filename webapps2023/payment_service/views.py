from decimal import Decimal
from django.shortcuts import render, redirect
import requests
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib import messages
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.contrib import messages
from .forms import RegisterForm, PaymentForm, AdminRegistrationForm
from .models import CustomUser, Transaction
from config import PORT, MODE

# Handles user registration.
def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            starting_currency = form.cleaned_data["currency"]

            if starting_currency != "GBP":
                conversion_url = f"{MODE}://localhost:{PORT}/currency_conversion/convert/"
                conversion_params = {
                    "source": "GBP",
                    "target": starting_currency,
                    "amount": 1000,
                }
                conversion_response = requests.get(conversion_url, params=conversion_params, verify=False)

                if conversion_response.status_code == 200:
                    user.balance = conversion_response.json()["converted_amount"]
                else:
                    messages.error(request, "Currency conversion failed.")
                    return render(request, 'payment_service/register.html', {'form': form})

            user.save()
            messages.success(request, 'Registration successful.')
            login(request, user)
            return redirect('payment_service:dashboard')
    else:
        form = RegisterForm()
    return render(request, 'payment_service/register.html', {'form': form})

# Just the dashboard page.
@login_required
def dashboard(request):
    return render(request, 'payment_service/dashboard.html')

# Handles sending payment from one user to another.
@login_required
def send_payment(request):
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            recipient_email = form.cleaned_data['recipient_email']
            current_user_email = request.user.email
            amount = form.cleaned_data["amount"]
            try:
                recipient = CustomUser.objects.get(email=recipient_email)
            except CustomUser.DoesNotExist:
                messages.error(request, f'User with email {recipient_email} does not exist.')
                return render(request, 'payment_service/send_payment.html', {'form': form})

            transaction = form.save(commit=False)
            transaction.sender = request.user
            transaction.recipient = recipient
            transaction.currency = request.user.currency

            is_request = form.cleaned_data['is_request']
            if is_request:
                if recipient_email == current_user_email:
                    messages.error(request, "You cannot send money or request payments from yourself.")
                    return render(request, "payment_service/send_payment.html", {"form": form})
                else: 
                    transaction.is_request = True
                    transaction.save()
                    messages.success(request, f'Requested payment from {transaction.recipient}.')
            else:
                converted_amount = amount
                if request.user.currency != recipient.currency:
                    source_currency = request.user.currency
                    target_currency = recipient.currency
                    converted_amount = Decimal(str(get_conversion_rate_api(request, source_currency, target_currency, amount)))
                    
                if amount <= 0:
                    messages.error(request, "You cannot send negative or zero amount.")
                    return render(request, "payment_service/send_payment.html", {"form": form})
                
                if recipient_email == current_user_email:
                    messages.error(request, "You cannot send money to yourself.")
                    return render(request, "payment_service/send_payment.html", {"form": form})

                if transaction.amount > transaction.sender.balance:
                    messages.error(request, f'Insufficient balance. Your current balance is {transaction.sender.balance} {transaction.currency}.')
                    return render(request, 'payment_service/send_payment.html', {'form': form})
                
                transaction.sender.balance -= transaction.amount
                transaction.recipient.balance += converted_amount
                transaction.save()
                transaction.sender.save()
                transaction.recipient.save()
                messages.success(request, f'Sent {transaction.amount} {transaction.currency} to {transaction.recipient}.')

            return redirect('payment_service:send_payment')
    else:
        form = PaymentForm(initial={'currency': request.user.currency})
    return render(request, 'payment_service/send_payment.html', {'form': form})

# API for currency conversion.
def get_conversion_rate_api(request, source_currency, target_currency, amount):
    conversion_url = f"{MODE}://localhost:{PORT}/currency_conversion/convert/"
    conversion_params = {
        "source": source_currency,
        "target": target_currency,
        "amount": amount,
        }
    conversion_response = requests.get(conversion_url, params=conversion_params, verify=False)
    if conversion_response.status_code == 200:
        return conversion_response.json()["converted_amount"]
    else:
        return messages.error(request, "Currency conversion failed.")

# Handles user accepting another user's payment request.  
@login_required
def accept_request(request, transaction_id):
    payment_request = get_object_or_404(Transaction, id=transaction_id, recipient=request.user, is_request=True)
    sender = payment_request.sender
    recipient = payment_request.recipient
    amount = payment_request.amount

    converted_amount = amount
    if sender.currency != recipient.currency:
        source_currency = sender.currency
        target_currency = recipient.currency
        converted_amount = Decimal(str(get_conversion_rate_api(request, source_currency, target_currency, amount)))

    if recipient.balance >= converted_amount:
        recipient.balance -= converted_amount
        sender.balance += amount
        recipient.save()
        sender.save()
        payment_request.is_completed = True

        # Record the completed transaction before deleting request notification. Swap sender and recipient.
        completed_transaction = Transaction(
            sender=recipient,
            recipient=sender,
            amount=amount,
            currency=sender.currency,
            is_request=False,
            is_completed=True
        )
        completed_transaction.save()
        
        payment_request.delete()
        messages.success(request, 'Payment request accepted.')
    else:
        messages.error(request, 'Insufficient balance to accept the request.')
    return redirect('payment_service:notifications')

# Handles user rejecting another user's payment request. 
@login_required
def reject_request(request, transaction_id):
    transaction = get_object_or_404(Transaction, pk=transaction_id, recipient=request.user, is_completed=False, is_request=True)
    transaction.delete()
    messages.success(request, f'Rejected payment request from {transaction.sender.username}.')
    return redirect('payment_service:notifications')

# Checks if user exist checking if that user's email exists. 
@login_required
def check_email(request):
    email = request.GET.get('email')
    if not email:
        return HttpResponse("Please enter an email address.")
    try:
        CustomUser.objects.get(email=email)
        return HttpResponse("User with this email exists.")
    except CustomUser.DoesNotExist:
        return HttpResponse("User with this email does not exist.")

# Just the notifications page.
@login_required
def notifications(request):
    user = request.user
    requests = Transaction.objects.filter(recipient=user, is_request=True).order_by('-timestamp')
    transactions = Transaction.objects.filter(Q(sender=user) | Q(recipient=user), is_request=False).order_by('-timestamp')
    return render(request, 'payment_service/notifications.html', {'requests': requests, 'transactions': transactions, 'user': user})

# Admin pages. Need superuser access.
@login_required
def admin_page(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('payment_service:dashboard')

    query = request.GET.get('search', '')
    if query:
        users = CustomUser.objects.filter(username__icontains=query)
    else:
        users = CustomUser.objects.all()

    return render(request, 'payment_service/admin_page.html', {'users': users})

# Admin pages. Viewing user transactions.
@login_required
def user_transactions(request, user_id):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('payment_service:dashboard')

    user = get_object_or_404(CustomUser, id=user_id)
    transactions = Transaction.objects.filter(Q(sender=user) | Q(recipient=user))

    return render(request, 'payment_service/user_transactions.html', {'user': user, 'transactions': transactions})

# Admin pages. Register another superuser.
def register_admin(request):
    if not request.user.is_superuser:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('payment_service:dashboard')

    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_superuser = True
            user.is_staff = True
            user.save()
            messages.success(request, 'Admin user has been created successfully.')
            return redirect('payment_service:dashboard')
    else:
        form = AdminRegistrationForm()

    return render(request, 'payment_service/register_admin.html', {'form': form})

