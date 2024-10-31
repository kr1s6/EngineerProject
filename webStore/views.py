from django.contrib.auth.decorators import login_required
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib import messages
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from .models import (User,
                     Address,
                     Category,
                     Product)
from .forms import (UserRegistrationForm,
                    UserLoginForm,
                    UserAddressForm,
                    CategoryCreationForm,
                    ProductCreationForm)


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
    template_name = 'registration/login.html'
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


class UserAddressCreationView(LoginRequiredMixin, FormView):
    model = Address
    form_class = UserAddressForm
    template_name = "form_base.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user  # current logged user

        if len(list(address.user.addresses.all())) >= 5:
            messages.error(
                self.request,
                "Not premium user can only have 5 addresses. Remove one before adding another one"
            )
            return self.form_invalid(form)

        if address.is_default:
            Address.objects.filter(
                user=self.request.user, is_default=True
            ).update(is_default=False)
        address.save()
        messages.success(
            self.request, f"Address {address.street} added successfully"
        )
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additional_fields = {
            "page_title": "Dodaj Adres",
            "header": "Podaj adres",
            "button_text": "Dodaj",
        }
        context.update(additional_fields)
        return context


# UserPassesTestMixin - only super-user have acess
class ProductCategoryCreationView(UserPassesTestMixin, CreateView):
    model = Category
    form_class = CategoryCreationForm
    template_name = "form_base.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additional_fields = {
            "page_title": "Dodaj Kategorię",
            "header": "Podaj Kategorie",
            "button_text": "Dodaj",
        }
        context.update(additional_fields)
        return context


class ProductCreationView(UserPassesTestMixin, CreateView):
    model = Product
    form_class = ProductCreationForm
    template_name = "form_base.html"
    success_url = reverse_lazy("home")

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, f"Product '{form.instance.name}' added successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additional_fields = {
            "page_title": "Dodaj Produkt",
            "header": "Podaj Product",
            "button_text": "Dodaj",
        }
        context.update(additional_fields)
        return context
