from collections import defaultdict
from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin)
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q, QuerySet, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin
from django.views.generic.edit import FormView

from .forms import (UserRegistrationForm,
                    UserLoginForm,
                    UserAddressForm,
                    PaymentMethodForm)
from .models import (User,
                     Address,
                     Category,
                     Product,
                     PaymentMethod,
                     Order,
                     UserQueryLog,
                     UserCategoryVisibility,
                     UserProductVisibility,
                     Cart,
                     CartItem,
                     Reaction, Rate)


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


class HomePageView(CategoriesMixin, ListView):
    model = Product
    template_name = "homePage/index.html"
    context_object_name = "products"

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = get_recommended_products(self.request.user)
        else:
            queryset = Product.objects.order_by('?')[:10]
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['tablets'] = Category.objects.filter(name="Tablety").first()
        context['speakers'] = Category.objects.filter(name="Głośniki komputerowe").first()
        context['laptops'] = Category.objects.filter(name="Laptopy").first()
        context['pc'] = Category.objects.filter(name="Komputery stacjonarne").first()
        return context


class AllProductsView(CategoriesMixin, ListView):
    model = Product
    template_name = "all_products.html"
    context_object_name = "products"

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        return context

    def get_queryset(self):
        queryset = Product.objects.all()

        # Sortowanie
        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating_asc':
            queryset = queryset.order_by('average_rate')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-average_rate')
        elif sort_by == 'popularity_asc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('popularity_count')
        elif sort_by == 'popularity_desc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('-popularity_count')

        # Filtrowanie po cenie
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset


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


class CartDetailView(CategoriesMixin, ListView):
    template_name = 'cart/cart_detail.html'
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

    def get_context_data(self, **kwargs):
        self.request.session.pop("order_session", None)
        if 'order_session' not in self.request.session:
            self.request.session['order_session'] = {
                'selected_address_id': None,
                'payment_method_id': None,
                'current_order_id': None,
            }
            self.request.session.modified = True

        context = super().get_context_data(**kwargs)
        cart_items = context['cart_items']
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        context['total_quantity'] = sum(item.quantity for item in cart_items)
        context['discount'] = 10
        context['total_amount'] = total_price

        for item in cart_items:
            filtered_details = {key: value for key, value in item.product.product_details.items() if value.strip()}
            item.product.filtered_details = dict(list(filtered_details.items())[:3])
        return context


class UserAddressCreationView(CategoriesMixin, LoginRequiredMixin, FormView):
    model = Address
    form_class = UserAddressForm
    template_name = "address_form.html"
    success_url = reverse_lazy("payment_form")

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user

        if form.cleaned_data.get('use_for_delivery'):
            Address.objects.filter(user=self.request.user, use_for_delivery=True).update(use_for_delivery=False)
            address.use_for_delivery = True

        address.save()

        order_session = self.request.session.get('order_session', {})
        order_session['selected_address_id'] = address.id
        self.request.session['order_session'] = order_session
        self.request.session.modified = True

        messages.success(self.request, f"Adres {address.street} został zapisany.")
        return super().form_valid(form)


class AddressSelectionView(LoginRequiredMixin, CategoriesMixin, View):
    template_name = "cart/address_selection.html"

    def get(self, request, *args, **kwargs):
        user_addresses = Address.objects.filter(user=request.user)

        if not user_addresses.exists():
            messages.info(request, "Nie masz jeszcze zapisanych adresów. Dodaj nowy adres.")
            return redirect('add_address')

        context = self.get_context_data()
        context['addresses'] = user_addresses
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_address_id = request.POST.get('selected_address')

        if selected_address_id:
            order_session = request.session.get('order_session', {})
            order_session['selected_address_id'] = selected_address_id
            request.session['order_session'] = order_session
            request.session.modified = True

            messages.success(request, "Adres został zapisany.")
            return redirect('payment_form')

        messages.error(request, "Proszę wybrać adres dostawy.")
        return redirect('address_selection')


class PaymentMethodView(CategoriesMixin, LoginRequiredMixin, FormView):
    template_name = "cart/payment_form.html"
    form_class = PaymentMethodForm
    success_url = reverse_lazy("order_summary")

    def form_valid(self, form):
        payment_method = form.save(commit=False)
        payment_method.user = self.request.user
        payment_method.save()

        order_session = self.request.session.get('order_session', {})
        order_session['payment_method_id'] = payment_method.id
        self.request.session['order_session'] = order_session
        self.request.session.modified = True

        messages.success(self.request, "Metoda płatności została zapisana.")
        return redirect('create_order')

    def form_invalid(self, form):
        messages.error(self.request, "Proszę popraw błędy w formularzu.")
        return super().form_invalid(form)


class OrderCreateView(CategoriesMixin, LoginRequiredMixin, View):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        return self.create_order(request)

    def get(self, request, *args, **kwargs):
        return self.create_order(request)

    def create_order(self, request):
        user = request.user
        cart = Cart.objects.filter(user=user).first()

        if not cart or not cart.items.exists():
            messages.error(request, "Twój koszyk jest pusty.")
            return redirect('cart_detail')

        order_session = request.session.get('order_session', {})
        selected_address_id = order_session.get('selected_address_id')
        selected_payment_method_id = order_session.get('payment_method_id')

        delivery_address = Address.objects.filter(id=selected_address_id, user=user).first()
        payment_method = PaymentMethod.objects.filter(id=selected_payment_method_id, user=user).first()

        if not delivery_address:
            messages.error(request, "Nie wybrano adresu dostawy.")
            return redirect('address_selection')

        if not payment_method:
            messages.error(request, "Nie wybrano metody płatności.")
            return redirect('payment_form')

        order = Order.objects.create(
            user=user,
            delivery_address=delivery_address,
            payment_method=payment_method,
            total_amount=cart.get_total_price(),
            status='created',
        )

        for item in cart.items.all():
            order.products.add(item.product)

        cart.items.all().delete()

        order_session['current_order_id'] = order.id
        request.session['order_session'] = order_session
        request.session.modified = True

        messages.success(request, "Zamówienie zostało utworzone.")
        return redirect('order_summary')


class OrderSummaryView(CategoriesMixin, LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        order_session = request.session.get('order_session', {})
        current_order_id = order_session.get('current_order_id')

        if not current_order_id:
            messages.error(request, "Brak zamówienia w trakcie realizacji.")
            return redirect('cart_detail')

        try:
            order = Order.objects.get(id=current_order_id, user=request.user)
        except Order.DoesNotExist:
            messages.error(request, "Nie znaleziono zamówienia.")
            return redirect('cart_detail')

        context = self.get_context_data()  # Get context from CategoriesMixin
        context['order'] = order
        context['products'] = order.products.all()
        context['delivery_address'] = order.delivery_address
        context['payment_method'] = order.payment_method
        return render(request, 'cart/order_summary.html', context)


class OrderDetailView(CategoriesMixin, LoginRequiredMixin, DetailView):
    model = Order
    template_name = "order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        return context


class OrderListView(CategoriesMixin, LoginRequiredMixin, ListView):
    model = Order
    template_name = "order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class HeaderContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['order'] = Order.objects.filter(user=self.request.user).last()
        return context


class ProductSearchView(CategoriesMixin, ListView):
    model = Product
    template_name = 'search.html'
    context_object_name = 'object_list'
    paginate_by = 16

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_queryset(self):
        query = self.request.GET.get('search_value')
        queryset = Product.objects.all()

        if query and len(query) >= 2:  # Minimalna długość zapytania to 2 znaki
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(brand__icontains=query) |
                Q(description__icontains=query) |
                Q(product_details__icontains=query)
            ).distinct()

        # Sortowanie
        sort_by = self.request.GET.get('sort_by')
        print(sort_by)
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating_asc':
            queryset = queryset.order_by('average_rate')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-average_rate')
        elif sort_by == 'popularity_asc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('popularity_count')
        elif sort_by == 'popularity_desc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('-popularity_count')

        # Filtrowanie po cenie
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        if not max_price and not min_price and not sort_by:
            if self.request.user.is_authenticated:
                UserQueryLog.objects.create(
                    user=self.request.user,
                    query=query,
                    query_date=datetime.now()
                )
            else:
                if 'query_log' not in self.request.session:
                    self.request.session['query_log'] = []

                self.request.session['query_log'].append({
                    'query': query,
                    'query_date': datetime.now().isoformat()
                })

                self.request.session.modified = True

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['total_products'] = Product.objects.count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        context['search_value'] = self.request.GET.get('search_value', '')

        return context


def product_like(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.user.is_authenticated:
        if request.user in product.liked_by.all():
            product.liked_by.remove(request.user)
            liked = False
            reaction, created = Reaction.objects.get_or_create(
                user=request.user,
                product=product,
                type='dislike'
            )
            reaction.assigned_date = timezone.now()
            reaction.save()
        else:
            product.liked_by.add(request.user)
            liked = True
            reaction, created = Reaction.objects.get_or_create(
                user=request.user,
                product=product,
                type='like'
            )
            reaction.assigned_date = timezone.now()
            reaction.save()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'likes_count': product.liked_by.count()})

    else:
        liked_products = request.session.get('liked_products', [])
        session_reactions = request.session.get('session_reactions', [])

        existing_reaction = next((r for r in session_reactions if r['product_id'] == product.id), None)

        if product.id in liked_products:
            liked_products.remove(product.id)
            liked = False
            if existing_reaction:
                existing_reaction['type'] = 'dislike'
                existing_reaction['date'] = str(timezone.now())
            else:
                session_reactions.append({
                    'product_id': product.id,
                    'type': 'dislike',
                    'date': str(timezone.now())
                })
        else:
            liked_products.append(product.id)
            liked = True
            if existing_reaction:
                existing_reaction['type'] = 'like'
                existing_reaction['date'] = str(timezone.now())
            else:
                session_reactions.append({
                    'product_id': product.id,
                    'type': 'like',
                    'date': str(timezone.now())
                })

        request.session['liked_products'] = liked_products
        request.session['session_reactions'] = session_reactions

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'liked': liked, 'likes_count': len(liked_products)})

    return redirect('index')


class FavoritesListView(CategoriesMixin, ListView):
    model = Product
    template_name = "favorites.html"
    context_object_name = "liked_products"
    paginate_by = 16

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
    paginate_by = 16

    def get_favorites(self):
        return get_liked_products(self.request)

    def get_queryset(self):
        category = get_object_or_404(Category, id=self.kwargs['category_id'])
        all_categories = [category]
        subcategories = category.subcategories.all()
        all_categories += list(subcategories)
        for subcategory in subcategories:
            all_categories += list(subcategory.subcategories.all())

        queryset = Product.objects.filter(categories__in=all_categories).distinct()

        sort_by = self.request.GET.get('sort_by')
        if sort_by == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort_by == 'price_desc':
            queryset = queryset.order_by('-price')
        elif sort_by == 'rating_asc':
            queryset = queryset.order_by('average_rate')
        elif sort_by == 'rating_desc':
            queryset = queryset.order_by('-average_rate')
        elif sort_by == 'popularity_asc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('popularity_count')
        elif sort_by == 'popularity_desc':
            queryset = queryset.annotate(popularity_count=Count('liked_by')).order_by('-popularity_count')

        # Filtrowanie po cenie
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        one_hour_ago = timezone.now() - timedelta(hours=1)

        if not max_price and not min_price and not sort_by:
            if self.request.user.is_authenticated:
                # Sprawdzenie, czy istnieje już wpis dla danej kategorii i użytkownika w ciągu ostatniej godziny
                if not UserCategoryVisibility.objects.filter(user=self.request.user, category=category,
                                                             view_date__gte=one_hour_ago).exists():
                    UserCategoryVisibility.objects.create(user=self.request.user, category=category,
                                                          view_date=timezone.now())
            else:
                if 'category_visibility' not in self.request.session:
                    self.request.session['category_visibility'] = []

                # Sprawdzenie, czy istnieje już wpis w sesji dla danej kategorii w ciągu ostatniej godziny
                session_entries = self.request.session['category_visibility']
                if not any(
                        entry['category'] == category.id and datetime.fromisoformat(entry['view_date']) >= one_hour_ago
                        for entry in session_entries):
                    session_entries.append({
                        'category': category.id,
                        'view_date': timezone.now().isoformat()
                    })

                self.request.session.modified = True
        return queryset

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
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        context['category'] = category
        return context


class ProductDetailView(CategoriesMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        product = self.get_object()
        one_hour_ago = timezone.now() - timedelta(hours=1)

        if request.user.is_authenticated:
            # Sprawdzenie, czy istnieje już wpis dla danego produktu i użytkownika w ciągu ostatniej godziny
            if not UserProductVisibility.objects.filter(user=request.user, product=product,
                                                        view_date__gte=one_hour_ago).exists():
                UserProductVisibility.objects.create(user=request.user, product=product, view_date=timezone.now())
        else:
            if 'product_visibility' not in request.session:
                request.session['product_visibility'] = []

            # Sprawdzenie, czy istnieje już wpis w sesji dla danego produktu w ciągu ostatniej godziny
            session_entries = request.session['product_visibility']
            if not any(entry['product'] == product.id and datetime.fromisoformat(entry['view_date']) >= one_hour_ago for
                       entry in session_entries):
                session_entries.append({
                    'product': product.id,
                    'view_date': timezone.now().isoformat()
                })

            request.session.modified = True

        return response


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
    html_message = render_to_string('email/cart_summary_email.html',
                                    {'user': user, 'cart': cart, 'items': items, 'product_images': product_images, })
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


def get_recommended_products(user):
    # Wagi dla różnych kryteriów
    WEIGHT_RATING = 5
    WEIGHT_LIKE = 4
    WEIGHT_VISIBILITY = 3
    WEIGHT_CATEGORY_VISIBILITY = 2
    WEIGHT_QUERY = 1

    # Zbierz dane użytkownika
    viewed_products = UserProductVisibility.objects.filter(user=user).values_list('product_id', flat=True)
    viewed_categories = UserCategoryVisibility.objects.filter(user=user).values_list('category_id', flat=True)
    rated_products = Rate.objects.filter(user=user).values_list('product_id', flat=True)
    liked_products = Reaction.objects.filter(user=user, type='like').values_list('product_id', flat=True)
    user_queries = UserQueryLog.objects.filter(user=user).values_list('query', flat=True)

    # Inicjalizuj słownik z punktacją produktów
    product_scores = defaultdict(int)

    # Dodaj punktacje za ocenione produkty
    for product_id in rated_products:
        product_scores[product_id] += WEIGHT_RATING

    # Dodaj punktacje za polubione produkty
    for product_id in liked_products:
        product_scores[product_id] += WEIGHT_LIKE

    # Dodaj punktacje za przeglądane produkty
    for product_id in viewed_products:
        product_scores[product_id] += WEIGHT_VISIBILITY

    # Dodaj punktacje za przeglądane kategorie i ich podkategorie
    related_categories = Category.objects.filter(
        Q(id__in=viewed_categories) | Q(parent__id__in=viewed_categories)
    ).distinct().values_list('id', flat=True)

    related_products = Product.objects.filter(categories__id__in=related_categories).distinct().values_list('id',
                                                                                                            flat=True)
    for product_id in related_products:
        product_scores[product_id] += WEIGHT_CATEGORY_VISIBILITY

    # Dodaj punktacje za produkty zgodne z zapytaniami użytkownika
    for query in user_queries:
        matching_products = Product.objects.filter(name__icontains=query).values_list('id', flat=True)
        for product_id in matching_products:
            product_scores[product_id] += WEIGHT_QUERY

    # Sortuj produkty według punktacji malejąco
    sorted_products = sorted(product_scores.items(), key=lambda item: item[1], reverse=True)
    recommended_product_ids = [product_id for product_id, score in sorted_products]

    # Pobierz obiekty produktów z bazy danych, ograniczając do 20
    recommended_products = Product.objects.filter(id__in=recommended_product_ids)[:20]

    return recommended_products
