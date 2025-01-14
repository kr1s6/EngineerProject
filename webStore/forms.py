import re

from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .constants import POSSIBLE_EMAIL_DOMAIN_TLD
from .models import (User,
                     Address,
                     PaymentMethod)


class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "birthday",
            "gender",
            "password",
        ]
        widgets = {
            "password": forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        if commit:
            user.username = self.generate_username(
                self.cleaned_data.get("first_name"), self.cleaned_data.get("last_name")
            )
            user.save()
        return user

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Email is already taken")
        elif "@" in email:
            domain = email.split("@")[1]
            if domain.split(".")[-1] not in POSSIBLE_EMAIL_DOMAIN_TLD:
                raise forms.ValidationError("Given email domain not recognized")
        return email

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        parsed_phone_number = re.sub(r'\D', '', phone_number)
        if len(parsed_phone_number) != 9:
            raise ValidationError("Phone number must have exactly 9 digits.")
        return parsed_phone_number

    @staticmethod
    def generate_username(first_name, last_name):
        first_name = first_name.lower()
        last_name = last_name.lower()

        if " " in first_name:
            first_name = "_".join(first_name.split())
        if " " in last_name:
            last_name = "_".join(last_name.split())

        username = f"{first_name}.{last_name}"
        num = 1

        while User.objects.filter(username=username).exists():
            username = f"{first_name}.{last_name}{num}"
            num += 1

        return username


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code', 'country', 'is_default']
        widgets = {
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_default': 'Ustaw jako domyślny adres',
        }

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('street'):
            self.add_error('street', "Ulica jest wymagana.")
        if not cleaned_data.get('city'):
            self.add_error('city', "Miasto jest wymagane.")
        if not cleaned_data.get('postal_code'):
            self.add_error('postal_code', "Kod pocztowy jest wymagany.")
        if not cleaned_data.get('country'):
            self.add_error('country', "Kraj jest wymagany.")
        return cleaned_data


class PaymentMethodForm(forms.ModelForm):
    class Meta:
        model = PaymentMethod
        fields = ['payment_method', 'card_number', 'expiration_date', 'cvv', 'blik_code']
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'card_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Wprowadź numer karty'}),
            'expiration_date': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/RR'}),
            'cvv': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'CVV'}),
            'blik_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Kod Blik'}),
        }
        labels = {
            'payment_method': 'Metoda płatności',
            'card_number': 'Numer karty',
            'expiration_date': 'Data ważności',
            'cvv': 'Kod CVV',
            'blik_code': 'Kod Blik',
        }

    def clean(self):
        cleaned_data = super().clean()
        payment_method = cleaned_data.get('payment_method')

        if payment_method == 'karta':
            required_fields = {
                'card_number': 'Numer karty jest wymagany dla metody Karta kredytowa/debetowa.',
                'expiration_date': 'Data ważności jest wymagana dla metody Karta kredytowa/debetowa.',
                'cvv': 'Kod CVV jest wymagany dla metody Karta kredytowa/debetowa.',
            }
            for field, error_message in required_fields.items():
                if not cleaned_data.get(field):
                    self.add_error(field, error_message)

        elif payment_method == 'blik':
            pass

        return cleaned_data
    
# Change Personal Data
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'birthday', 'phone_number']

class ChangePasswordForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Aktualne hasło",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nowe hasło",
        required=True
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Potwierdź nowe hasło",
        required=True
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current_password = self.cleaned_data.get('current_password')
        if not authenticate(username=self.user.username, password=current_password):
            raise forms.ValidationError("Aktualne hasło jest nieprawidłowe.")
        return current_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise forms.ValidationError("Nowe hasła muszą być takie same.")
        return cleaned_data

class ChangeEmailForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Potwierdź hasło",
        required=True
    )

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not authenticate(username=self.user.username, password=password):
            raise forms.ValidationError("Hasło jest nieprawidłowe.")
        return password