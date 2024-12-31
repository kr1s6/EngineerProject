import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.template.defaultfilters import default
from django.utils import timezone
from django.utils.timezone import now
from engineerProject import settings
from .constants import *
from django.db.models.signals import post_save
from django.dispatch import receiver
import time


# username | firstname | last name  | password inherited by AbstractUser
class User(AbstractUser):
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=15, null=False, blank=False)
    is_admin = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10, choices=[(gender.value, gender.name.capitalize()) for gender in UserGender],
        default=UserGender.MALE.value
    )

    def __str__(self):
        return f"User {self.first_name} {self.last_name} {self.email} \tGender: {self.gender})"


class Address(models.Model):
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='addresses'
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)
    use_for_delivery = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.street}, {self.city}, {self.country} ({self.user.email})"


class PaymentMethod(models.Model):
    PAYMENT_CHOICES = [
        ('karta', 'Karta kredytowa/debetowa'),
        ('blik', 'Blik'),
        ('za_pobraniem', 'Płatność za pobraniem'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payment_methods")
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_CHOICES,
        default='karta'
    )
    card_number = models.CharField("Numer karty", max_length=16, blank=True, null=True)
    expiration_date = models.CharField("Data ważności", max_length=5, blank=True, null=True)  # MM/YY
    cvv = models.CharField("Kod CVV", max_length=4, blank=True, null=True)
    blik_code = models.CharField("Kod Blik", max_length=6, blank=True, null=True)

    def __str__(self):
        return f"{self.payment_method} for {self.user.username}"



class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    parent = models.ManyToManyField(
        'self', blank=True, symmetrical=False, related_name='subcategories'
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"

    def __str__(self):
        return f"Category: {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, default='KMG')
    image = models.ImageField(upload_to='products/', default='products/default_product.png')
    description = models.TextField()
    price = models.DecimalField(max_digits=100, decimal_places=2)
    average_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    liked_by = models.ManyToManyField(User, related_name='favorites', blank=True)
    categories = models.ManyToManyField(Category, related_query_name='products')
    product_details = models.JSONField(default=dict)
    product_images_links = models.JSONField(default=dict)

    def __str__(self):
        return (f"Product: {self.name}, Brand: {self.brand}, Description: {self.description}"
                f"\nPrice: {self.price}. Avg: {self.average_rate}")

    def clean(self):
        if not os.path.exists(os.path.join(settings.MEDIA_ROOT, self.image.name)):
            raise ValidationError(f"The image {self.image.name} does not exist.")

    def update_average_rate(self):
        """Recalculate and update the average rate for the product."""
        ratings = self.ratings.all()  # Related name for Rate model should be "ratings"
        if ratings.exists():
            self.average_rate = round(ratings.aggregate(models.Avg('value'))['value__avg'], 2)
        else:
            self.average_rate = None  # Jeśli brak ocen
        self.save()

class Order(models.Model):
    STATUS_CHOICES = [
        ('created', 'Utworzono'),
        ('processing', 'Przetwarzane'),
        ('in_delivery', 'W dostawie'),
        ('ready_for_pickup', 'Gotowe do odbioru'),
        ('completed', 'Zakończone'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    products = models.ManyToManyField(Product, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='created')
    created_at = models.DateTimeField(auto_now_add=True)
    delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    payment_method = models.ForeignKey(
        PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders"
    )
    total_amount = models.DecimalField(default=0.0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Zamówienie #{self.id} ({self.user.username}) - {self.status}"


class Rate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='ratings')
    value = models.IntegerField()  # Oceny w zakresie 1-5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name}: {self.value}"


class Reaction(models.Model):
    REACTION_CHOICES = [('like', 'Like'), ('dislike', 'Dislike')]
    user = models.ForeignKey(
        'User', on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        'Product', on_delete=models.CASCADE
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    def __str__(self):
        return f"{self.user.first_name} - {self.product.name}: {self.type}"


class UserProductVisibility(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    view_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} vued {self.product.name} on {self.view_date}"


class UserCategoryVisibility(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    view_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} vued {self.category.name} on {self.view_date}"


class UserQueryLog(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    query = models.CharField(max_length=255)
    query_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.query} on {self.query_date}"


class Cart(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True, related_name='carts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart {self.id} for {self.user.username} - Created at: {self.created_at}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey('Cart', on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Cart {self.cart.id}"

    def get_total_price(self):
        return self.product.price * self.quantity


class RecommendedProducts(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, null=True, blank=True)
    products = models.ManyToManyField(Product, related_name='recomended_products')