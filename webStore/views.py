from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import (authenticate,
                                 login,
                                 logout)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin)
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import QuerySet
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.csrf import csrf_exempt
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
                     Reaction,
                     Rate,
                     RecommendedProducts)


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
    paginate_by = 16

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
    template_name = 'cart_order/cart.html'
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
    template_name = "cart_order/add_address.html"
    success_url = reverse_lazy("address_selection")

    def form_valid(self, form):
        address = form.save(commit=False)
        address.user = self.request.user

        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
            address.is_default = True

        address.save()

        order_session = self.request.session.get('order_session', {})
        order_session['selected_address_id'] = address.id
        self.request.session['order_session'] = order_session
        self.request.session.modified = True

        messages.success(self.request, f"Adres {address.street} został zapisany.")
        return super().form_valid(form)


class AddressSelectionView(CategoriesMixin, LoginRequiredMixin, View):
    template_name = "cart_order/address_selection.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        user_addresses = Address.objects.filter(user=request.user)

        if not user_addresses.exists():
            messages.info(request, "Nie masz jeszcze zapisanych adresów. Dodaj nowy adres.")
            return redirect('add_address')

        default_address = user_addresses.filter(is_default=True).first()
        context['addresses'] = user_addresses
        context['default_address_id'] = default_address.id if default_address else None

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        selected_address_id = request.POST.get('selected_address')

        if selected_address_id:
            Address.objects.filter(user=request.user, is_default=True).update(is_default=False)
            Address.objects.filter(id=selected_address_id, user=request.user).update(is_default=True)

            order_session = request.session.get('order_session', {})
            order_session['selected_address_id'] = selected_address_id
            request.session['order_session'] = order_session
            request.session.modified = True

            messages.success(request, "Adres został zapisany.")
            return redirect('payment_form')

        messages.error(request, "Proszę wybrać adres dostawy.")
        return redirect('address_selection')


class PaymentMethodView(CategoriesMixin, LoginRequiredMixin, FormView):
    template_name = "cart_order/payment.html"
    form_class = PaymentMethodForm

    def form_valid(self, form):
        payment_method = form.save(commit=False)
        payment_method.user = self.request.user
        payment_method.save()

        # Zapisz wybraną metodę płatności w sesji
        order_session = self.request.session.get('order_session', {})
        order_session['payment_method_id'] = payment_method.id
        self.request.session['order_session'] = order_session
        self.request.session.modified = True

        # Przekierowanie do Blik lub podsumowania
        if payment_method.payment_method == "blik":
            return redirect('blik_code')  # Przekierowanie na stronę wprowadzania kodu Blik
        else:
            return redirect('create_order')  # Dla innych metod płatności

    def form_invalid(self, form):
        messages.error(self.request, "Proszę poprawić błędy w formularzu.")
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class BlikCodeView(CategoriesMixin, LoginRequiredMixin, View):
    template_name = "cart_order/blik_payment.html"

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        blik_code = request.POST.get('blik_code')

        if not blik_code or len(blik_code) != 6 or not blik_code.isdigit():
            messages.error(request, "Nieprawidłowy kod Blik. Spróbuj ponownie.")
            return render(request, self.template_name)  # Renderuj ponownie stronę z błędem

        # Zapisz kod Blik w sesji
        order_session = request.session.get('order_session', {})
        order_session['blik_code'] = blik_code
        request.session['order_session'] = order_session
        request.session.modified = True

        messages.success(request, "Płatność Blik została zatwierdzona.")
        return redirect('create_order')


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
        blik_code = order_session.get('blik_code')

        if not delivery_address:
            messages.error(request, "Nie wybrano adresu dostawy.")
            return redirect('address_selection')

        if not payment_method:
            messages.error(request, "Nie wybrano metody płatności.")
            return redirect('payment_form')

        if payment_method.payment_method == 'blik' and not blik_code:
            messages.error(request, "Nie podano kodu Blik.")
            return redirect('blik_code')

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

        # sendin email with appreciation of buying items
        send_order_confirmation_email(order)
        messages.success(request, "Zamówienie zostało utworzone.")
        return redirect('order_detail', pk=order.id)


class OrderDetailView(CategoriesMixin, LoginRequiredMixin, DetailView):
    model = Order
    template_name = "cart_order/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['products'] = self.object.products.all()
        context['can_rate'] = self.object.status == 'completed'
        return context


def get_order_status(request, order_id):
    if request.user.is_authenticated:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        return JsonResponse({'status': order.status})
    return JsonResponse({'error': 'Unauthorized'}, status=401)

class OrderListView(CategoriesMixin, LoginRequiredMixin, ListView):
    model = Order
    template_name = "cart_order/order_list.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


@csrf_exempt
def rate_product(request, product_id, rating_id=None):
    if request.method == "POST":
        product = get_object_or_404(Product, id=product_id)
        user = request.user
        value = int(request.POST.get('value', 0))
        comment = request.POST.get('comment', '')

        if not (1 <= value <= 5):
            return JsonResponse({'error': 'Invalid rating value'}, status=400)

        if rating_id:  # update existing rate
            rate = get_object_or_404(Rate, id=rating_id, user=user, product=product)
            rate.value = value
            rate.comment = comment
            rate.save()
            created = False
            message = 'Rating updated'
        else:  # creating new rate
            rate = Rate.objects.create(
                user=user,
                product=product,
                value=value,
                comment=comment
            )
            created = True
            message = 'Rating created'

        # update average rate based on new/changed rate
        product.update_average_rate()

        return JsonResponse({
            'message': message,
            'created': created,
            'average_rate': product.average_rate,
            'rating_count': product.ratings.count(),
            'user_rating': {
                'value': rate.value,
                'comment': rate.comment
            }
        })
    return JsonResponse({'error': 'Invalid request method'}, status=400)

def get_ratings_html(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    ratings = product.ratings.all().order_by('-created_at')

    html = render_to_string('rating_list.html', {'ratings': ratings, 'user': request.user})
    return JsonResponse({'html': html})

# function to send ordr confirmation
def send_order_confirmation_email(order):
    subject = f"Dziękujemy za zamówienie #{order.id} w KMG Store"
    html_message = render_to_string('email/order_confirmation_email.html', {
        'user': order.user,
        'order': order,
        'delivery_address': order.delivery_address,
        'payment_method': order.payment_method,
        'total_amount': order.total_amount,
        'products': order.products.all(),
    })
    plain_message = strip_tags(html_message)
    from_email = 'kmgstoreproject@gmail.com'
    to_email = order.user.email

    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
    )


def send_status_update_email(order):
    subject = f"Aktualizacja statusu zamówienia #{order.id}"
    context = {
        'user': order.user,
        'order': order,
        'status_display': dict(Order.STATUS_CHOICES).get(order.status, order.status),
    }
    html_message = render_to_string('email/order_status_update.html', context)
    plain_message = strip_tags(html_message)
    from_email = 'your_email@example.com'
    recipient_list = [order.user.email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_products'] = self.get_queryset().count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        context['search_value'] = self.request.GET.get('search_value', '')
        return context

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = get_object_or_404(Category, id=self.kwargs['category_id'])
        context['total_products'] = self.get_queryset().count()
        context['liked_products'] = get_liked_products(self.request)
        context['liked_product_ids'] = list(self.get_favorites().values_list('id', flat=True))
        context['min_price'] = self.request.GET.get('min_price', '')
        context['max_price'] = self.request.GET.get('max_price', '')
        context['sort_by'] = self.request.GET.get('sort_by', 'default')
        context['category'] = category
        return context

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


class ProductDetailView(CategoriesMixin, DetailView):
    model = Product
    template_name = 'product_detail.html'
    context_object_name = 'product'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        product = self.get_object()
        one_hour_ago = timezone.now() - timedelta(hours=1)

        # Rejestrowanie widoczności produktu (bez zmian)
        if request.user.is_authenticated:
            if not UserProductVisibility.objects.filter(user=request.user, product=product,
                                                        view_date__gte=one_hour_ago).exists():
                UserProductVisibility.objects.create(user=request.user, product=product, view_date=timezone.now())
        else:
            if 'product_visibility' not in request.session:
                request.session['product_visibility'] = []

            session_entries = request.session['product_visibility']
            if not any(entry['product'] == product.id and datetime.fromisoformat(entry['view_date']) >= one_hour_ago
                       for entry in session_entries):
                session_entries.append({
                    'product': product.id,
                    'view_date': timezone.now().isoformat()
                })
            request.session.modified = True

        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        context['ratings'] = product.ratings.all().order_by('-created_at')
        context['ratings_count'] = product.ratings.count()
        return context


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


from collections import defaultdict
from django.db.models import Q, Count


def get_recommended_products(user):
    # Wagi dla różnych kryteriów
    WEIGHT_RATING = 5
    WEIGHT_LIKE = 4
    WEIGHT_VISIBILITY = 3
    WEIGHT_CATEGORY_VISIBILITY = 2
    WEIGHT_QUERY = 1
    WEIGHT_SAME_CATEGORY = 1  # Waga dla produktów w tej samej kategorii co polubione
    WEIGHT_INTERESTED = 3
    WEIGHT_SIMILAR_NAME = 1
    WEIGHT_SIMILAR_CATEGORY = 1
    WEIGHT_LIKED_SIMILAR_NAME = 2
    WEIGHT_LIKED_SIMILAR_CATEGORY = 1
    WEIGHT_OTHER_USER_LIKED = 15

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

    # Dodaj dodatkowe punkty dla produktów z tej samej kategorii co polubione
    liked_categories = Category.objects.filter(products__in=liked_products).distinct().values_list('id', flat=True)
    products_in_liked_categories = Product.objects.filter(categories__id__in=liked_categories).distinct().values_list(
        'id', flat=True)

    for product_id in products_in_liked_categories:
        if product_id not in liked_products:  # Unikaj podwójnego punktowania polubionych produktów
            product_scores[product_id] += WEIGHT_SAME_CATEGORY

    # Sprawdź, czy istnieje rekord RecommendedProducts dla danego użytkownika
    try:
        recommended_products_instance = RecommendedProducts.objects.get(user=user)
        previous_recommended_products = recommended_products_instance.products.all()

        # Dodaj punkty za zainteresowane produkty
        for product in previous_recommended_products:
            if product.id in viewed_products:
                product_scores[product.id] += WEIGHT_INTERESTED

                # Dodaj punkty za produkty z podobnymi słowami w nazwie
                similar_products = Product.objects.filter(name__icontains=product.name).values_list('id', flat=True)
                for similar_product_id in similar_products:
                    product_scores[similar_product_id] += WEIGHT_SIMILAR_NAME

                # Dodaj punkty za produkty z tymi samymi kategoriami
                same_category_products = Product.objects.filter(
                    categories__in=product.categories.all()).distinct().values_list('id', flat=True)
                for same_category_product_id in same_category_products:
                    product_scores[same_category_product_id] += WEIGHT_SIMILAR_CATEGORY

            # Dodaj punkty za polubione produkty
            if product.id in liked_products:
                # Dodaj punkty za produkty z podobnymi słowami w nazwie
                similar_products = Product.objects.filter(name__icontains=product.name).values_list('id', flat=True)
                for similar_product_id in similar_products:
                    product_scores[similar_product_id] += WEIGHT_LIKED_SIMILAR_NAME

                # Dodaj punkty za produkty z tymi samymi kategoriami
                same_category_products = Product.objects.filter(
                    categories__in=product.categories.all()).distinct().values_list('id', flat=True)
                for same_category_product_id in same_category_products:
                    product_scores[same_category_product_id] += WEIGHT_LIKED_SIMILAR_CATEGORY
    except RecommendedProducts.DoesNotExist:
        # Jeśli rekord nie istnieje, nic nie rób
        pass

    # Znajdź użytkowników, którzy mają minimum dwa takie same polubione produkty co użytkownik
    other_users = User.objects.filter(
        reaction__product__in=liked_products,
        reaction__type='like'
    ).annotate(same_likes=Count('reaction__product')).filter(same_likes__gte=2).exclude(id=user.id).distinct()

    for other_user in other_users:
        # Pobierz produkty, które ten użytkownik polubił
        other_user_liked_products = Reaction.objects.filter(user=other_user, type='like').values_list('product_id',
                                                                                                      flat=True)

        for other_user_product_id in other_user_liked_products:
            # Sprawdź, czy istnieje reakcja "unlike" dla tego produktu przez tego użytkownika
            unlike_reaction = Reaction.objects.filter(user=other_user, type='dislike',
                                                      product_id=other_user_product_id).first()

            # Jeśli istnieje reakcja "unlike", porównaj daty reakcji "like" i "unlike"
            if unlike_reaction:
                like_reaction = Reaction.objects.filter(user=other_user, type='like',
                                                        product_id=other_user_product_id).first()
                if like_reaction and unlike_reaction.assigned_date >= like_reaction.assigned_date:
                    continue  # Pomijamy produkt, jeśli reakcja "unlike" ma późniejszą lub taką samą datę jak "like"

            # Jeśli produkt nie został "unlikowany" później, dodaj punkty
            if other_user_product_id not in liked_products:
                product_scores[other_user_product_id] += WEIGHT_OTHER_USER_LIKED

    # Sortuj produkty według punktacji malejąco
    sorted_products = sorted(product_scores.items(), key=lambda item: item[1], reverse=True)
    recommended_product_ids = [product_id for product_id, score in sorted_products]
    recommended_products = []
    for product_id in recommended_product_ids[:20]:
        product = Product.objects.get(id=product_id)
        if not product.liked_by.filter(id=user.id).exists():
            recommended_products.append(product)

    # Dodaj rekomendowane produkty do modelu RecommendedProducts
    recommended_products_instance, created = RecommendedProducts.objects.get_or_create(user=user)
    recommended_products_instance.products.set(recommended_products)
    recommended_products_instance.save()

    return recommended_products
