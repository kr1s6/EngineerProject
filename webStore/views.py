from collections import defaultdict
from datetime import datetime, timedelta
from threading import Thread

from django.contrib import messages
from django.contrib.auth import (authenticate,
                                 login,
                                 logout, update_session_auth_hash)
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import (LoginRequiredMixin)
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import QuerySet, Q, Count
from django.http import JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.html import strip_tags
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView
from django.views.generic.base import ContextMixin, TemplateView
from django.views.generic.edit import FormView
from django.urls import reverse
from .forms import (UserRegistrationForm,
                    UserLoginForm,
                    UserAddressForm,
                    PaymentMethodForm, UserEditForm, ChangePasswordForm, ChangeEmailForm)
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
                     RecommendedProducts,
                     Message, Conversation, UserRecommendedProductInteraction)


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
            if not queryset:
                queryset = Product.objects.order_by('?')[:10]
        else:
            queryset = get_recommended_products_from_session(self.request.session)
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


class UserProfileView(CategoriesMixin, LoginRequiredMixin, View):
    template_name = "profile.html"

    def get(self, request, *args, **kwargs):
        # Przygotowanie formularzy
        form = UserEditForm(instance=request.user)
        password_form = ChangePasswordForm(user=request.user)
        email_form = ChangeEmailForm(user=request.user, instance=request.user)

        # Pobranie kontekstu z CategoriesMixin
        context = self.get_context_data()
        context.update({
            "form": form,
            "password_form": password_form,
            "email_form": email_form
        })

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        if 'update_profile' in request.POST:
            form = UserEditForm(request.POST, instance=request.user)
            password = request.POST.get("password")
            user = authenticate(username=request.user.username, password=password)

            if user and form.is_valid():
                form.save()
                messages.success(request, "Dane zostały zaktualizowane.")
            elif not user:
                messages.error(request, "Hasło jest nieprawidłowe.")
            else:
                messages.error(request, "Wystąpił błąd podczas aktualizacji.")

        elif 'change_email' in request.POST:
            email_form = ChangeEmailForm(request.POST, user=request.user, instance=request.user)
            if email_form.is_valid():
                email_form.save()
                messages.success(request, "E-mail został zaktualizowany.")
            else:
                messages.error(request, "Wystąpił błąd podczas aktualizacji e-maila.")

        elif 'change_password' in request.POST:
            password_form = ChangePasswordForm(request.POST, user=request.user)
            if password_form.is_valid():
                new_password = password_form.cleaned_data.get('new_password')
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Hasło zostało zmienione.")
            else:
                messages.error(request, "Wystąpił błąd podczas zmiany hasła.")

        return redirect("user_profile")

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form_fields'] = [
            {'name': 'street', 'label': 'Ulica', "placeholder": "Wprowadź swoją ulice"},
            {'name': 'city', 'label': 'Miasto', "placeholder": "Wprowadź swoje miasto" },
            {'name': 'postal_code', 'label': 'Kod pocztowy',  "placeholder": "Wprowadź kod pocztowy miasta"},
            {'name': 'country', 'label': 'Kraj',  "placeholder": "Wprowadź swój kraj"}
        ]
        return context


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

        admin_user = User.objects.filter(username="admin", is_superuser=True).first()
        # conversation about order statuses
        status_conversation, created = Conversation.objects.get_or_create(
            order=order,
            is_admin_conversation=True,
        )
        status_conversation.participants.add(user, admin_user)
        if created:
            Message.objects.create(
                conversation=status_conversation,
                sender=admin_user,
                content=f"Twoje zamówienie zostało utworzone. Obecny status: {order.get_status_display()}."
            )
        # general conversation with admi about order
        general_conversation,created  = Conversation.objects.get_or_create(
            order=order,
            is_admin_conversation=False
        )
        general_conversation.participants.add(user, admin_user)
        if created:
            Message.objects.create(
                conversation=general_conversation,
                sender=admin_user,
                content=(
                    f"Dziękujemy za złożenie"
                    f"<a href='{reverse('order_detail', args=[order.id])}' style='color: #1d68a7; font-weight: bold; text-decoration: underline;'> zamówienia #{order.id}</a>! "
                    "Jeśli masz jakieś pytania, skontaktuj się z nami tutaj."
                )
            )

        Thread(target=send_order_confirmation_email, args=(order,)).start()
        messages.success(request, "Zamówienie zostało utworzone.")
        return redirect('order_detail', pk=order.id)


class OrderDetailView(CategoriesMixin, LoginRequiredMixin, DetailView):
    model = Order
    template_name = "cart_order/order_detail.html"
    context_object_name = "order"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            # Admin ma dostęp do wszystkich zamówień
            return Order.objects.all()
        # Użytkownik ma dostęp tylko do swoich zamówień
        return Order.objects.filter(user=user)

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


class MessagesListView(CategoriesMixin, LoginRequiredMixin, TemplateView):
    template_name = 'messages/messages_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        if user.is_superuser:
            conversations = Conversation.objects.filter(is_admin_conversation=False)
            conversation_data = [
                {
                    'id': conversation.id,
                    'participant': conversation.participants.exclude(id=user.id).first().username if conversation.participants.exclude(id=user.id).exists() else "Brak uczestnika",
                    'order_id': conversation.order.id if conversation.order else None,
                }
                for conversation in conversations
            ]
        else:
            conversations = Conversation.objects.filter(participants=user)
            conversation_data = [
                {
                    'id': conversation.id,
                    'order_id': conversation.order.id if conversation.order else None,
                    'is_status': conversation.is_admin_conversation,
                }
                for conversation in conversations
            ]

        last_conversation_id = None
        if hasattr(user, 'profile') and user.profile.last_opened_conversation:
            last_conversation_id = user.profile.last_opened_conversation.id

        context.update({
            'conversations': conversation_data,
            'last_conversation_id': last_conversation_id,
            'is_admin': user.is_superuser,
        })
        return context


@login_required
def load_messages(request, conversation_id):
    """Załaduj wiadomości dla wybranej konwersacji."""
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    # Zaktualizuj ostatnio otwartą konwersację
    profile = request.user.profile
    profile.last_opened_conversation = conversation
    profile.save()

    messages = conversation.messages.order_by('timestamp')

    return JsonResponse({
        'messages': [
            {
                'id': message.id,
                'content': message.content,
                'timestamp': message.timestamp.strftime('%H:%M'),
                'sender': message.sender.username if message.sender else 'System'
            }
            for message in messages
        ]
    })


@login_required
def fetch_new_messages(request, conversation_id):
    """Zwróć nowe wiadomości dla wybranej konwersacji."""
    last_message_id = int(request.GET.get('last_message_id', 0))
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    new_messages = conversation.messages.filter(id__gt=last_message_id).order_by('timestamp')

    # Sprawdź, czy status zamówienia to 'completed'
    is_completed = False
    if conversation.order:
        is_completed = conversation.order.status == 'completed'
    elif request.user.is_superuser:
        is_completed = True

    if new_messages.exists():
        return JsonResponse({
            'new_messages': [
                {
                    'id': message.id,
                    'content': message.content,
                    'timestamp': message.timestamp.strftime('%H:%M'),
                    'sender': message.sender.username if message.sender else 'System'
                }
                for message in new_messages
            ],
            'is_completed': is_completed
        })
    else:
        pass
    return JsonResponse({'new_messages': [], 'is_completed': is_completed})


@login_required
def save_last_opened_conversation(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

    profile = request.user.profile
    profile.last_opened_conversation = conversation
    profile.save()

    return JsonResponse({'status': 'success'})


@login_required
def send_message(request):
    """Obsługa wysyłania wiadomości w wybranej konwersacji."""
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content')

        conversation = get_object_or_404(Conversation, id=conversation_id, participants=request.user)

        Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content.strip()
        )

        return JsonResponse({'message': 'Wiadomość wysłana!'})
    return JsonResponse({'error': 'Nieprawidłowa metoda'}, status=400)


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


def get_similar_products(product):
    # Znajdź podobne produkty na podstawie kategorii i słów kluczowych w nazwie.
    similar_products_by_category = Product.objects.filter(
        categories__in=product.categories.all()
    ).exclude(id=product.id).distinct()

    similar_products_by_name = Product.objects.filter(
        name__icontains=product.name.split()[0]
    ).exclude(id=product.id).distinct()

    similar_products = similar_products_by_category | similar_products_by_name
    return similar_products.distinct()


def get_recommended_products(user):
    WEIGHT_CATEGORY_VISIBILITY = 1  # Waga dla produktów z wyświetlanych kategorii
    WEIGHT_LIKED_SIMILAR_PRODUCT = 2  # Waga dla podobnych produktów do polubionych
    WEIGHT_PURCHASED_SIMILAR_PRODUCT = 5  # Waga dla podobnych produktów do kupionych
    WEIGHT_QUERY = 4
    WEIGHT_OTHER_USERS_LIKE = 2
    WEIGHT_VIEVED_SIMILAR_PRODUCT = 1 # Waga dla produktów podobnych do wyświetlanych przez użykownika
    WEIGHT_OTHER_USERS_BUY = 8 # Waga dla produktów które kupili użykkownicy po kupnie tego samego
    WEIGHT_OTHER_USERS_BUY_LIKE = 5 # Waga dla produtków które kupili użytkownicy z takimi samymi polubieniami
    WEIGHT_PURCHASED_SIMILAR_PRODUCT_RECOMMENDED = 5  # Waga dla podobnych produktów do kupionych i wcześniej polecanych
    WEIGHT_VIEWED_AFTER_RECOMMENDATION = 3  # Waga dla produktów wyświetlonych po poleceniu
    WEIGHT_VIEWED_SIMILAR_AFTER_RECOMMENDATION = 2  # Waga dla podobnych produktów wyświetlonych po poleceniu
    WEIGHT_LIKED_SIMILAR_AFTER_RECOMMENDATION = 3  # Waga dla polubionych podobnych produktów po poleceniu

    product_scores = defaultdict(int)
    seven_days_ago = timezone.now() - timedelta(days=7)
    user_queries = UserQueryLog.objects.filter(user=user).values_list('query', flat=True)
    liked_products = Product.objects.filter(liked_by=user).values_list('id', flat=True)

    # Pobierz liczbę wyświetleń dla każdej kategorii przez użytkownika w ciągu ostatnich 7 dni
    viewed_categories = (
        UserCategoryVisibility.objects.filter(
            user=user,
            view_date__gte=seven_days_ago
        )
        .values('category_id')
        .annotate(view_count=Count('id'))
    )

    # Pobierz listę kupionych produktów przez użytkownika
    purchased_products = (
        Order.objects.filter(
            user=user,
            status='completed',
            created_at__gte=seven_days_ago
        )
        .values('products')
        .annotate(purchase_count=Count('products'))
    )

    liked_by_products = Product.objects.filter(liked_by=user)  # Produkty polubione przez użytkownika

    # Znajdź użytkowników, którzy kupili dokładnie ten sam produkt co użytkownik
    other_users_same_purchase = Order.objects.filter(
        user__in=User.objects.exclude(id=user.id),
        status='completed',
        products__in=liked_products
    ).values_list('user', flat=True).distinct()

    for other_user_id in other_users_same_purchase:
        similar_purchased_products = Order.objects.filter(
            user=other_user_id,
            status='completed'
        ).exclude(products__in=purchased_products).values_list('products', flat=True)

        for product_id in similar_purchased_products:
            product_scores[product_id] += WEIGHT_OTHER_USERS_BUY

    # Znajdź użytkowników, którzy mają minimum dwa takie same polubione produkty co użytkownik
    other_users = User.objects.filter(
        reaction__product__in=liked_products,
        reaction__type='like'
    ).annotate(same_likes=Count('reaction__product')).filter(same_likes__gte=2).exclude(id=user.id).distinct()

    for other_user in other_users:
        purchased_by_other_user = Order.objects.filter(user=other_user, status='completed').values_list('products',
                                                                                                        flat=True)
        for product_id in purchased_by_other_user:
            product_scores[product_id] += WEIGHT_OTHER_USERS_BUY_LIKE

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
                product_scores[other_user_product_id] += WEIGHT_OTHER_USERS_LIKE

    # Dodaj punktacje za produkty zgodne z zapytaniami użytkownika
    for query in user_queries:
        matching_products = Product.objects.filter(name__icontains=query).values_list('id', flat=True)
        for product_id in matching_products:
            product_scores[product_id] += WEIGHT_QUERY

    # Dla każdego polubionego produktu, znajdź podobne produkty i dodaj punkty
    for product in liked_by_products:
        similar_products = get_similar_products(product)  # Funkcja generująca podobne produkty
        for similar_product in similar_products:
            product_scores[similar_product.id] += WEIGHT_LIKED_SIMILAR_PRODUCT

    # Dodaj punkty dla produktów z wyświetlanych kategorii i podobnych
    for entry in viewed_categories:
        category_id = entry['category_id']
        view_count = entry['view_count']

        # Znajdź produkty związane z tą kategorią
        category_products = Product.objects.filter(categories__id=category_id).distinct()
        for product in category_products:
            product_scores[product.id] += WEIGHT_CATEGORY_VISIBILITY * view_count

    # Dodaj punkty za zakupione produkty i podobne
    for entry in purchased_products:
        product_id = entry['products']
        purchase_count = entry['purchase_count']

        # Znajdź podobne produkty
        similar_products = get_similar_products(Product.objects.get(id=product_id))
        for similar_product in similar_products:
            product_scores[similar_product.id] += WEIGHT_PURCHASED_SIMILAR_PRODUCT * purchase_count

    user_viewed_products = UserProductVisibility.objects.filter(
        user=user,
        view_date__gte=seven_days_ago)

    # Dodaj punkty za produkty wyświetlone po poleceniu
    for product in user_viewed_products:
        similar_products = get_similar_products(product.product)  # Funkcja generująca podobne produkty
        for similar_product in similar_products:
            product_scores[similar_product.id] += WEIGHT_VIEVED_SIMILAR_PRODUCT

    # Sprawdź, czy użytkownik kliknął polecany produkt
    try:
        recommended_products_instance = RecommendedProducts.objects.get(user=user)
        recommended_product_ids = recommended_products_instance.products.values_list('id', flat=True)
        added_at = recommended_products_instance.added_at

        viewed_products = UserProductVisibility.objects.filter(
            user=user,
            product_id__in=recommended_product_ids,
            view_date__gte=added_at
        ).values_list('product_id', flat=True)

        liked_products = Reaction.objects.filter(
            user=user,
            product_id__in=recommended_product_ids,
            type='like',
            assigned_date__gte=added_at
        ).values_list('product_id', flat=True)

        purchased_products = Order.objects.filter(
            user=user,
            products__in=recommended_product_ids,
            status='completed',
            created_at__gte=added_at
        ).values_list('products', flat=True)

        # Dodaj punkty za produkty wyświetlone po poleceniu
        for product_id in viewed_products:
            product_scores[product_id] += WEIGHT_VIEWED_AFTER_RECOMMENDATION

        # Dodaj punkty za podobne produkty wyświetlone po poleceniu
        for product_id in viewed_products:
            similar_products = get_similar_products(Product.objects.get(id=product_id))
            for similar_product in similar_products:
                product_scores[similar_product.id] += WEIGHT_VIEWED_SIMILAR_AFTER_RECOMMENDATION

        # Dodaj punkty za podobne produkty, które użytkownik polubił po poleceniu
        for product_id in liked_products:
            similar_products = get_similar_products(Product.objects.get(id=product_id))
            for similar_product in similar_products:
                product_scores[similar_product.id] += WEIGHT_LIKED_SIMILAR_AFTER_RECOMMENDATION

        # Dodaj punkty za podobne produkty zakupione po poleceniu
        for product_id in purchased_products:
            similar_products = get_similar_products(Product.objects.get(id=product_id))
            for similar_product in similar_products:
                product_scores[similar_product.id] += WEIGHT_PURCHASED_SIMILAR_PRODUCT_RECOMMENDED

        # Zapisz interakcje z polecanymi produktami
        for product_id in viewed_products:
            UserRecommendedProductInteraction.objects.create(
                user=user,
                product_id=product_id,
                interaction_type='view'
            )

        for product_id in liked_products:
            UserRecommendedProductInteraction.objects.create(
                user=user,
                product_id=product_id,
                interaction_type='like'
            )
        for product_id in purchased_products:
            UserRecommendedProductInteraction.objects.create(
                user=user,
                product_id=product_id,
                interaction_type='buy'
            )

    except RecommendedProducts.DoesNotExist:
        pass

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
    recommended_products_instance.added_at = timezone.now()
    recommended_products_instance.save()

    if not recommended_products:
        # Losowanie 20 produktów w przypadku pustej listy
        recommended_products = list(Product.objects.all().order_by('?')[:20])

    return recommended_products


def get_recommended_products_from_session(session):
    WEIGHT_LIKED_PRODUCT_SIMILAR = 3  # Waga dla polubionych produktów
    WEIGHT_VIEWED_PRODUCT = 2  # Waga dla wyświetlonych produktów
    WEIGHT_VIEWED_PRODUCT_SIMILAR = 1  # Waga dla wyświetlonych produktów
    WEIGHT_QUERY = 3  # Waga dla zapytań w sesji
    WEIGHT_CATEGORY_VISIBILITY = 2  # Waga dla widoczności kategorii
    WEIGHT_OTHER_USERS_LIKE = 3  # Waga dla produktów polubionych przez innych użytkowników
    WEIGHT_OTHER_USERS_BUY = 4  # Waga dla produktów kupionych przez użytkowników o podobnych polubieniach

    product_scores = defaultdict(int)

    # Polubione produkty z sesji
    liked_product_ids = list(session.get('liked_products', []))
    for product_id in liked_product_ids:
        similar_products = get_similar_products(Product.objects.get(id=product_id))  # Funkcja do podobnych produktów
        for similar_product in similar_products:
            product_scores[similar_product.id] += WEIGHT_LIKED_PRODUCT_SIMILAR

    # Wyświetlone produkty z sesji
    viewed_entries = session.get('product_visibility', [])
    for entry in viewed_entries:
        product_id = entry['product']
        product_scores[product_id] += WEIGHT_VIEWED_PRODUCT

        # Dodaj punkty dla podobnych produktów do wyświetlanego
        similar_products = get_similar_products(Product.objects.get(id=product_id))
        for similar_product in similar_products:
            product_scores[similar_product.id] += WEIGHT_VIEWED_PRODUCT_SIMILAR

    # Zapytania z sesji
    query_logs = session.get('query_log', [])
    for query in query_logs:
        matching_products = Product.objects.filter(name__icontains=query['query']).values_list('id', flat=True)
        for product_id in matching_products:
            product_scores[product_id] += WEIGHT_QUERY

    # Widoczność kategorii z sesji
    category_visibility = session.get('category_visibility', [])
    for category_id in category_visibility:
        category_products = Product.objects.filter(categories__id=category_id['category']).distinct()
        for product in category_products:
            product_scores[product.id] += WEIGHT_CATEGORY_VISIBILITY

    # Znalezienie użytkowników, którzy mają co najmniej dwa te same polecane produkty
    other_users_same_recommendations = Reaction.objects.filter(
        product_id__in=liked_product_ids,
        type='like'
    ).values_list('user', flat=True).annotate(similar_count=Count('product')).filter(similar_count__gte=2).distinct()
    for user_id in other_users_same_recommendations:
        user_liked_products = Product.objects.filter(reaction__user=user_id, reaction__type='like')
        for product in user_liked_products:
            product_scores[product.id] += WEIGHT_OTHER_USERS_LIKE

        # Kupione produkty przez użytkowników o podobnych polubieniach
        similar_purchased_products = Order.objects.filter(
            user=user_id,
            status='completed',
        ).values_list('products', flat=True)
        for product_id in similar_purchased_products:
            product_scores[product_id] += WEIGHT_OTHER_USERS_BUY

    # Filtracja polecanych produktów, które nie są polubione w sesji
    recommended_products = []
    for product_id in sorted(product_scores, key=product_scores.get, reverse=True):
        if product_id not in liked_product_ids:
            recommended_products.append(Product.objects.get(id=product_id))
            if len(recommended_products) >= 20:
                break

    if not recommended_products:
        # Losowanie 20 produktów w przypadku pustej listy
        recommended_products = list(Product.objects.all().order_by('?')[:20])

    return recommended_products


