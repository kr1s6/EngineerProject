from django.contrib import admin
from .forms import UserRegistrationForm
from .models import (User,
                     Category,
                     Product,
                     Rate,
                     Order,
                     Reaction,
                     UserProductVisibility,
                     Address,
                     Cart,
                     CartItem,
                     PaymentMethod,
                     UserCategoryVisibility,
                     UserQueryLog, RecommendedProducts)


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name')


admin.site.register(User, UserAdmin)

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('street', 'city', 'postal_code', 'country', 'user', 'is_default')

    def save_model(self, request, obj, form, change):
        if obj.is_default:
            # Jeśli adres jest oznaczony jako domyślny, ustaw pozostałe adresy użytkownika na `is_default=False`
            Address.objects.filter(user=obj.user, is_default=True).update(is_default=False)
        super().save_model(request, obj, form, change)

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_method', 'card_number', 'expiration_date', 'cvv')
    list_filter = ('payment_method',)
    search_fields = ('user__username', 'card_number')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'list_parents') 
    search_fields = ('name', 'parent__name')  
    filter_horizontal = ('parent',)  

    def list_parents(self, obj):
        """Wyświetlanie nadrzędnych kategorii w list_display"""
        return ", ".join([parent.name for parent in obj.parent.all()])
    list_parents.short_description = "Parent Categories"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')
    search_fields = ('name',)


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'value', 'created_at')
    search_fields = ('user__username', 'product__name')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'products')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'type', 'assigned_date')
    list_filter = ('type',)
    search_fields = ('user__username', 'product__name')


@admin.register(UserProductVisibility)
class UserProductVisibilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'view_date')
    search_fields = ('user__username', 'product__name')



class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'updated_at')
    inlines = [CartItemInline]

admin.site.register(Cart, CartAdmin)
admin.site.register(UserQueryLog)
admin.site.register(UserCategoryVisibility)
admin.site.register(RecommendedProducts)