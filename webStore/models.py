import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from .constants import *


# username | firstname | last name  | password inherited by AbstractUser
class User(AbstractUser):
    email = models.EmailField(unique=True)
    birthday = models.DateField(null=True, blank=True)
    registration_date = models.DateTimeField(default=timezone.now)
    phone_number = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_admin = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10, choices=[ (gender.value, gender.name.capitalize()) for gender in UserGender],
        default=UserGender.MALE.value
    )

    def __str__(self):
        return f"User {self.first_name} {self.last_name} {self.email} \tGender: {self.gender})"

    # object validation before saving into db1
    def clean(self):
        super().clean()
        # phone number validation
        if not (re.match(PHONE_NUMBER_PATTERNS['dashed'], self.phone_number) or
                re.match(PHONE_NUMBER_PATTERNS['together'], self.phone_number)):
            raise ValidationError(
                f"Phone number must follow {PHONE_NUMBER_PATTERNS['dashed']} | {PHONE_NUMBER_PATTERNS['together']} pattern")

        if "@" in self.email:
            domain = self.email.split("@")[1]
            if domain.split(".")[-1] not in POSSIBLE_EMAIL_DOMAIN_TLD:
                raise ValidationError("Given TLD not recognized")
        else:
            raise ValidationError("Email address has to contain at sign")

        # to be sure that Krzysiu/Maciej won't assign something different
        if self.gender not in [gender.value for gender in UserGender]:
            print(self.gender)
            raise ValidationError(f"{self.gender} is not valid gender")


class Address(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='addresses'
    )
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.country} ({self.user.email})"


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(
        User, related_name="categories"
    )

    def __str__(self):
        return f"Category {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='products/', default='products/default_product.png')
    description = models.TextField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    average_rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return (f"Product: {self.name}, {self.description}"
                f"\nPrice: {self.price}. Avg: {self.average_rate}")


class Rate(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="ratings",
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="ratings"
    )
    value = models.IntegerField()
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")  # user can only rate product once

    def __str__(self):
        return f"User: {self.user.name} rate {self.product.name} with {self.value}"


# TODO implement mecanic that user is assigned after choosing some products
class Order(models.Model):
    #TODO change to Enum version from constasnts.py
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_delivery', 'In Delivery'),
        ('delivered', 'Delivered'),
    ]

    # Primary user should have been assigned to any order
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True
    )
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f'Order {self.id} by {self.user.name} - Status: {self.status}'


# Many-to-many relation with additional field quantity
class OrderProduct(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='order_products'
    )
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name='order_products'
    )
    quantity = models.PositiveIntegerField(default=1)


class Reaction(models.Model):
    REACTION_CHOICES = [('like', 'Like'), ('dislike', 'Dislike')]
    user = models.OneToOneField(
        User, on_delete=models.CASCADE
    )
    product = models.OneToOneField(
        Product, on_delete=models.CASCADE
    )
    assigned_date = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    def __str__(self):
        return f"{self.user.name} - {self.product.name}: {self.type}"


class UserProductVisibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    view_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} viewed {self.product.name} on {self.view_date}"


class UserReactionVisibility(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    view_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} reacted to {self.reaction.product.name} on {self.view_date}"
