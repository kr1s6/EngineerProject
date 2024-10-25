from django.shortcuts import render

from .forms import UserRegistrationForm
from django.contrib import messages
from django.shortcuts import render, redirect


def home(request):
    return render(request, "index.html")


def register_user(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():  # run clean methods for form and model validation
            user = form.save(commit=False)
            user.set_password(
                form.cleaned_data['password']
            )  # password hash
            user.save()
            messages.success(
                request, f"User {user.username} registered successfully"
            )
            return redirect("login")
    else:
        form = UserRegistrationForm()
    return render(request,
                  "registration/register.html",
                  {"form": form}
                  )
