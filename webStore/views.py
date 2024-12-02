from django.contrib.auth.decorators import login_required
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.views.generic import ListView
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


class HomeProductsListView(ListView):
    model = Product
    template_name = "index.html"
    context_object_name = "products"
    paginate_by = 20

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class UserRegisterView(FormView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save(commit=True)
        messages.success(self.request, f"Registered successfully")
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Submitted Data:", self.request.POST)
        return super().form_invalid(form)


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
                messages.success(self.request, "Login successfully")
                return super().form_valid(form)
            else:
                form.add_error(None, "Incorrect email or password")
        except User.DoesNotExist:
            form.add_error('email', "No user found with the given email address")
        return self.form_invalid(form)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Logout successfully")
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
            "page_title": "Add Address",
            "header": "Add Address",
            "button_text": "Submit",
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
            "page_title": "Add Category",
            "header": "Add Categories",
            "button_text": "Submit",
        }
        context.update(additional_fields)
        return context

    def form_valid(self, form):
        parents = form.cleaned_data.get('parent')
        if parents.exists():
            parent_names = ", ".join([parent.name for parent in parents])
            messages.success(
                self.request,
                f"Subcategory '{form.instance.name}' added under '{parent_names}' successfully!"
            )
        else:
            messages.success(
                self.request,
                f"Category '{form.instance.name}' added successfully!"
            )
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Submitted Data:", self.request.POST)
        print("Cleaned Data:", form.cleaned_data)
        return super().form_invalid(form)


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

    def form_invalid(self, form):
        print("Submitted Data:", self.request.POST)
        print("Cleaned Data:", form.cleaned_data)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        additional_fields = {
            "page_title": "Add Product",
            "header": "Add Product",
            "button_text": "Submit",
        }
        context.update(additional_fields)
        return context

class ProductSearchView(ListView):
    model = Product
    template_name = 'search.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        query = self.request.GET.get('search_value')
        if query:
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(description__icontains=query)
            ).distinct()
        return Product.objects.all()