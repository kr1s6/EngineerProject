from django.contrib import messages
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        UserPassesTestMixin)
from django.db.models import Q, QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormView, CreateView
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
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


class CategoriesMixin(ContextMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(parent__isnull=True)
        selected_category_id = self.request.GET.get('category')
        if selected_category_id:
            try:
                selected_category = Category.objects.get(id=selected_category_id)
                context['subcategories'] = selected_category.subcategories.all()
                context['selected_category'] = selected_category
            except Category.DoesNotExist:
                context['subcategories'] = None
                context['selected_category'] = None
        else:
            context['subcategories'] = None
            context['selected_category'] = None
        return context


class HomeProductsListView(CategoriesMixin, ListView):
    model = Product
    template_name = "index.html"
    context_object_name = "products"
    paginate_by = 15

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        return context


class UserRegisterView(CategoriesMixin, FormView):
    template_name = "registration/register.html"
    form_class = UserRegistrationForm
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save(commit=True)

        messages.success(self.request, f"Registered successfully")
        send_registration_email(form.cleaned_data['email'], form.cleaned_data['first_name'])
        return super().form_valid(form)

    def form_invalid(self, form):
        print("Submitted Data:", self.request.POST)
        return super().form_invalid(form)


class UserLoginView(CategoriesMixin, FormView):
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


class UserAddressCreationView(CategoriesMixin, LoginRequiredMixin, FormView):
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
        return

    # UserPassesTestMixin - only super-user have acess


class ProductCategoryCreationView(CategoriesMixin, UserPassesTestMixin, CreateView):
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


class ProductCreationView(CategoriesMixin, UserPassesTestMixin, CreateView):
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


class ProductSearchView(CategoriesMixin, ListView):
    model = Product
    template_name = 'search.html'
    context_object_name = 'object_list'
    paginate_by = 15

    def get_queryset(self):
        query = self.request.GET.get('search_value')
        if query and len(query) >= 2:  # Minimalna długość zapytania to 2 znaki
            return Product.objects.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(description__icontains=query)
            ).distinct()
        return Product.objects.none()

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
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


class FavoritesListView(CategoriesMixin, ListView):
    model = Product
    template_name = "favorites.html"
    context_object_name = "liked_products"
    paginate_by = 15

    def get_queryset(self):
        return get_liked_products(self.request)

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['total_liked_products'] = self.get_queryset().count()
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


class AddToCartView(CategoriesMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        # Pobierz quantity z danych POST lub ustaw na 1, jeśli nie ma
        quantity = int(request.POST.get('quantity', 1))

        if request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart, created = Cart.objects.get_or_create(id=cart_id, user=None)
            else:
                cart = Cart.objects.create(user=None)
                request.session['cart_id'] = cart.id

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()

        # Jeśli żądanie jest asynchroniczne (AJAX)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'product_id': product_id, 'quantity': cart_item.quantity})

        return redirect('cart_detail')


class CartDetailView(CategoriesMixin, ListView):
    template_name = 'cart_detail.html'
    context_object_name = 'cart_items'

    def get_queryset(self):
        if self.request.user.is_authenticated:
            cart, created = Cart.objects.get_or_create(user=self.request.user)
        else:
            cart_id = self.request.session.get('cart_id')
            if cart_id:
                try:
                    cart = Cart.objects.get(id=cart_id, user=None)
                except Cart.DoesNotExist:
                    cart = None
            else:
                cart = None

        if cart:
            return CartItem.objects.filter(cart=cart)
        else:
            return CartItem.objects.none()


class RemoveFromCartView(CategoriesMixin, View):
    def post(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = get_object_or_404(Cart, id=cart_id, user=None)
            else:
                return JsonResponse({'success': False, 'message': 'Cart not found'})

        cart_item = get_object_or_404(CartItem, cart=cart, product=product)
        cart_item.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'product_id': product_id})
        return redirect('cart_detail')


class UpdateCartItemViewBack(CategoriesMixin, View):
    def post(self, request, product_id):
        action = request.POST.get('action')
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            send_cart_summary(request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = get_object_or_404(Cart, id=cart_id, user=None)
            else:
                return JsonResponse({'success': False, 'message': 'Cart not found'})

        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        if action == 'increase':
            cart_item.quantity += 1
        elif action == 'decrease' and cart_item.quantity > 1:
            cart_item.quantity -= 1
        cart_item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'product_id': product_id, 'quantity': cart_item.quantity})
        return redirect('cart_detail')


class UpdateCartItemView(CategoriesMixin, View):
    def post(self, request, product_id):
        action = request.POST.get('action')
        quantity = request.POST.get('quantity')
        product = get_object_or_404(Product, id=product_id)

        if request.user.is_authenticated:
            cart = get_object_or_404(Cart, user=request.user)
            send_cart_summary(request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = get_object_or_404(Cart, id=cart_id, user=None)
            else:
                return JsonResponse({'success': False, 'message': 'Cart not found'})

        cart_item = get_object_or_404(CartItem, cart=cart, product=product)

        if quantity:  # Jeżeli quantity jest podane w żądaniu
            try:
                new_quantity = int(quantity)
                if new_quantity < 1:
                    return JsonResponse({'success': False, 'message': 'Quantity must be at least 1'})
                cart_item.quantity = new_quantity
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid quantity value'})
        else:  # Jeśli nie ma quantity, to sprawdzamy akcję
            if action == 'increase':
                cart_item.quantity += 1
            elif action == 'decrease' and cart_item.quantity > 1:
                cart_item.quantity -= 1

        cart_item.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'product_id': product_id, 'quantity': cart_item.quantity})
        return redirect('cart_detail')



class CategoryProductsView(ListView, CategoriesMixin):
    model = Product
    template_name = 'category_products.html'
    context_object_name = 'products'
    paginate_by = 15

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_queryset(self):
        category = get_object_or_404(Category, id=self.kwargs['category_id'])
        all_categories = [category]
        subcategories = category.subcategories.all()
        all_categories += list(subcategories)
        for subcategory in subcategories:
            all_categories += list(subcategory.subcategories.all())

        return Product.objects.filter(categories__in=all_categories).distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, id=self.kwargs['category_id'])

        all_categories = [category]
        subcategories = category.subcategories.all()
        all_categories += list(subcategories)
        for subcategory in subcategories:
            all_categories += list(subcategory.subcategories.all())

        total_products = Product.objects.filter(categories__in=all_categories).distinct().count()

        context['total_products'] = total_products
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['category'] = category
        return context


class ProductDetailView(CategoriesMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'


def send_cart_summary(user):
    cart = Cart.objects.filter(user=user).last()
    if not cart:
        return
    items = CartItem.objects.filter(cart=cart)
    product_images = []

    for item in items:
        if item.product.product_images_links:
            product_images[item.product.id] = item.product.product_images_links[0]
        else:
            product_images[item.product.id] = None
    subject = 'Twoje zamówienie w naszym sklepie'
    html_message = render_to_string('email/cart_summary_email.html', {'user': user, 'cart': cart, 'items': items, 'product_images': product_images,})
    plain_message = strip_tags(html_message)
    from_email = 'kmgstoreproject@gmail.com'
    to = user.email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)


def send_registration_email(email, user):
    subject = 'Rejestracja w KMG Store'
    html_message = render_to_string('email/registration_email.html', {'user': user})
    plain_message = strip_tags(html_message)
    from_email = 'kmgstoreproject@gmail.com'
    to = email

    send_mail(subject, plain_message, from_email, [to], html_message=html_message)