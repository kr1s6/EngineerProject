from django.contrib import admin
from .forms import UserRegistrationForm
from .models import (User,
                     Category,
                     Product,
                     Rate,
                     Order,
                     OrderProduct,
                     Reaction,
                     UserProductVisibility,
                     UserReactionVisibility,
                     Address)


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_admin')
    search_fields = ('email', 'first_name', 'last_name')


admin.site.register(User, UserAdmin)
admin.site.register(Address)


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
    list_display = ('id', 'user', 'order_date', 'status')
    search_fields = ('user__username',)
    list_filter = ('status',)


@admin.register(OrderProduct)
class OrderProductAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity')
    search_fields = ('order__id', 'product__name')


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'type', 'assigned_date')
    list_filter = ('type',)
    search_fields = ('user__username', 'product__name')


@admin.register(UserProductVisibility)
class UserProductVisibilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'view_date')
    search_fields = ('user__username', 'product__name')


@admin.register(UserReactionVisibility)
class UserReactionVisibilityAdmin(admin.ModelAdmin):
    list_display = ('user', 'reaction', 'view_date')
    search_fields = ('user__username', 'reaction__product__name')
