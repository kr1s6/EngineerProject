from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from .forms import UserRegistrationForm, UserLoginForm
from .models import User


def home(request):
    return render(request, "index.html")


class UserRegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        user = form.save(commit=True)
        messages.success(self.request, f"User {user.username} registered successfully")
        return super().form_valid(form)


class UserLoginView(FormView):
    template_name = 'login.html'
    form_class = UserLoginForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password')

        try:
            user = User.objects.get(email=email)
            username = user.username

            user = authenticate(self.request, username=username, password=password)
            if user is not None:
                login(self.request, user)
                messages.success(self.request, "Zalogowano pomyślnie")
                return super().form_valid(form)
            else:
                messages.error(self.request, "Nieprawidłowe dane logowania")
        except User.DoesNotExist:
            messages.error(self.request, "Nie znaleziono użytkownika z podanym adresem email")

        return self.form_invalid(form)


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")