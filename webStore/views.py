from django.contrib import messages
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView
from django.views.generic.edit import FormView, CreateView

from .forms import (UserRegistrationForm,
                    UserLoginForm,
                    UserAddressForm,
                    CategoryCreationForm,
                    ProductCreationForm)
from .models import (Cart, CartItem)
from .models import (User,
                     Address,
                     Category,
                     Product)


class HomeProductsListView(ListView):
    model = Product
    template_name = "index.html"
    context_object_name = "products"
    paginate_by = 25

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
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
                sync_session_likes_to_user(self.request)
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_products'] = Product.objects.count()
        return context


def product_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        if request.user in product.liked_by.all():
            product.liked_by.remove(request.user)
            liked = False
        else:
            product.liked_by.add(request.user)
            liked = True
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'likes_count': product.liked_by.count()})

    else:
        liked_products = request.session.get('liked_products', [])
        if product.id in liked_products:
            liked_products.remove(product.id)
            liked = False
        else:
            liked_products.append(product.id)
            liked = True
        request.session['liked_products'] = liked_products
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'likes_count': len(liked_products)})

    return redirect('index')


class FavoritesListView(ListView):
    model = Product
    template_name = "favorites.html"
    context_object_name = "liked_products"
    paginate_by = 25

    def get_queryset(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['total_liked_products'] = self.get_queryset().count()
        context['liked_product_ids'] = list(self.get_queryset().values_list('id', flat=True))
        return context

def get_liked_products(request) -> QuerySet:
    if request.user.is_authenticated:
        return request.user.favorites.all()
    else:
        liked_products_ids = request.session.get('liked_products', [])
        return Product.objects.filter(id__in=liked_products_ids)

def sync_session_likes_to_user(request):
    if request.user.is_authenticated:
        liked_products = request.session.get('liked_products', [])
        user = request.user
        for product_id in liked_products:
            try:
                product = Product.objects.get(id=product_id)
                if product not in user.favorites.all():
                    user.favorites.add(product)
            except Product.DoesNotExist:
                continue
        request.session['liked_products'] = []


class AddToCartView(View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()

        return JsonResponse({'success': True, 'product_id': product_id, 'quantity': cart_item.quantity})


def product_detail(request):
    return None
