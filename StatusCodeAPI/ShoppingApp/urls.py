"""
URL configuration for Amazon Customer Status Tracker project.

This module defines all URL routes for the application, mapping URLs to their respective view functions.
The project consists of two main components:
1. Shopping App - Simulates an e-commerce shopping experience
2. Status Tracker - Tracks and visualizes the status of shopping operations

For more information on Django URL configuration, see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path
from shoppingapp import views as shop_views
from statustracker import views as tracker_views

urlpatterns = [
    # Django Admin Interface
    path('admin/', admin.site.urls),
    
    # Shopping App URLs - Customer-facing e-commerce functionality
    # Main shopping flow
    path('', shop_views.index, name='index'),  # Homepage with featured products
    path('amazon/', shop_views.amazon_selection, name='amazon_selection'),  # Select Amazon as platform
    path('categories/', shop_views.category_list, name='category_list'),  # Browse all product categories
    path('category/<int:category_id>/', shop_views.product_list, name='product_list'),  # List products in a category
    path('product/<int:product_id>/', shop_views.product_detail, name='product_detail'),  # View product details
    
    # Cart and checkout process
    path('add-to-cart/<int:product_id>/', shop_views.add_to_cart, name='add_to_cart'),  # Add product to cart
    path('cart/', shop_views.cart_view, name='cart_view'),  # View shopping cart contents
    path('clear-cart/', shop_views.clear_cart, name='clear_cart'),  # Clear all items from cart
    path('checkout/', shop_views.checkout, name='checkout'),  # Complete purchase
    path('order/<int:order_id>/', shop_views.order_confirmation, name='order_confirmation'),  # Order confirmation
    
    # Testing and demonstration - removed failure guide
    
    # Status Tracker URLs - Admin-facing analytics and monitoring
    path('dashboard/', tracker_views.dashboard, name='dashboard'),  # Visual dashboard of operation statistics
    path('stats/', tracker_views.get_stats, name='stats'),  # API endpoint for operation statistics data
]