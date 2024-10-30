from django import forms

from .models import User, Category


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
            "gender": forms.Select(
                attrs={"class": "form-control", "style": "width: 100px !important"}
            ),
            "birthday": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)  # Haszowanie hasła przed zapisaniem
        if commit:
            user.username = f'{user.first_name}.{user.last_name}'
            user.save()
        return user

    # init that add bootstrap class to every registration widget
    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(f"Email {email} is already taken")
        else:
            return email


class UserLoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)