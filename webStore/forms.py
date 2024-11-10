import re

from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from .constants import POSSIBLE_EMAIL_DOMAIN_TLD
from .models import (User,
                     Address,
                     Category,
                     Product)


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
            user.username = f"{user.first_name}.{user.last_name}"
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


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)


class UserAddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'city', 'postal_code', 'country', 'is_default']
        widgets = {
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_default': 'Ustaw jako domyślny',
        }


class CategoryCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['description'].required = False

    class Meta:
        model = Category
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required")

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Description is required")


class ProductCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for field in ['name', 'image', 'description', 'price', 'categories']:
            self.fields[field].required = False

    class Meta:
        model = Product
        fields = ['name', 'image', 'description', 'price', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'style': 'max-width: 250px'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = {
            'name': "Name is required",
            'image': "Image is required",
            'description': "Description is required",
            'price': "Price is required",
            'categories': "Categories are required",
        }
        for field, error_message in required_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error_message)
        return cleaned_data