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
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'is_default': 'Ustaw jako domyślny',
        }


class CategoryCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].required = True
        self.fields['description'].required = True
        self.fields['parent'].queryset = Category.objects.all()
        self.fields['parent'].widget = forms.SelectMultiple(
            attrs={
                'class': 'form-control',
                'size': '5', 
            }
        )
        self.fields['parent'].label = "Subcategories" 

                
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise forms.ValidationError("Name is required")
        return name

    def clean_description(self):
        description = self.cleaned_data.get('description')
        if not description:
            raise forms.ValidationError("Description is required")
        return description

    def clean_parent(self):
        parents = self.cleaned_data.get('parent')
        if parents:
            for parent in parents:
                if parent.parent.exists():  # Sprawdź, czy wybrany rodzic ma inne nadrzędne kategorie
                    raise forms.ValidationError(
                        f"Subcategories cannot have subcategories. '{parent.name}' is already a subcategory."
                    )
        return parents


class ProductCreationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ModelForm, self).__init__(*args, **kwargs)
        for field in ['name', 'brand', 'image', 'description', 'price', 'categories']:
            self.fields[field].required = False

    class Meta:
        model = Product
        fields = ['name', 'brand', 'image', 'description', 'price', 'categories']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'price': forms.TextInput(attrs={'class': 'form-control', 'style': 'max-width: 250px'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        required_fields = {
            'name': "Name is required",
            'brand': "Brand is required",
            'image': "Image is required",
            'description': "Description is required",
            'price': "Price is required",
            'categories': "Categories are required",
        }
        for field, error_message in required_fields.items():
            if not cleaned_data.get(field):
                self.add_error(field, error_message)
        return cleaned_data