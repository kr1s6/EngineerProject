from django import forms

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
            user.set_password(password)  # Haszowanie hasła przed zapisaniem
        if commit:
            user.username = f"{user.first_name}.{user.last_name}"
            user.save()
        return user

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Email {email} is already taken")
        else:
            return email


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
    class Meta:
        model = Category
        fields = ['name', 'description']


class ProductCreationForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'image', 'description', 'price', 'categories']
        widgets = {
            'categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
