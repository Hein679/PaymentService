from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Transaction
from django.core.validators import MinValueValidator

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'currency')

class PaymentForm(forms.ModelForm):
    # amount = forms.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
    recipient_email = forms.EmailField(required=True, label="Recipient's Email")
    is_request = forms.BooleanField(initial=False, required=False, label="Request Payment")

    class Meta:
        model = Transaction
        fields = ('amount', 'recipient_email', 'currency', 'is_request')

class AdminRegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
