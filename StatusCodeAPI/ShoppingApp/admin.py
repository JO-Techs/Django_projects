"""
Shopping Application Admin Configuration

This module configures the Django admin interface for the shopping application models.
It defines how models are displayed, filtered, and edited in the admin interface.
"""

from django.contrib import admin
from .models import Category, Product, Cart, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for the Category model."""
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    """Admin configuration for the Product model."""
    list_display = ('name', 'category', 'price', 'stock')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    
    fieldsets = (
        (None, {
            'fields': ('name', 'category', 'description')
        }),
        ('Pricing and Inventory', {
            'fields': ('price', 'stock')
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
    )


class CartItemInline(admin.TabularInline):
    """Inline admin for CartItem to be displayed within Cart admin."""
    model = CartItem
    extra = 0
    readonly_fields = ('total_price',)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for the Cart model."""
    list_display = ('customer_id', 'created_at', 'updated_at', 'item_count', 'cart_total')
    search_fields = ('customer_id',)
    inlines = [CartItemInline]
    
    def item_count(self, obj):
        """Return the number of items in the cart."""
        return obj.items.count()
    item_count.short_description = 'Items'
    
    def cart_total(self, obj):
        """Calculate and return the total value of the cart."""
        total = sum(item.total_price for item in obj.items.all())
        return f"${total:.2f}"
    cart_total.short_description = 'Total'


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem to be displayed within Order admin."""
    model = OrderItem
    extra = 0
    readonly_fields = ('price',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for the Order model."""
    list_display = ('id', 'customer_id', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('customer_id', 'id')
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        (None, {
            'fields': ('customer_id', 'status', 'total_amount')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at')