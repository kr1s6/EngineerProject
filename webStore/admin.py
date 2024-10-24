from django.contrib import admin

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
    list_display = ('id', 'name', 'description')  # Kolumny, które będą widoczne w liście
    search_fields = ('name',)


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
