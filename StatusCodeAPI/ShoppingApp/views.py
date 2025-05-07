"""
Shopping Application Views

This module provides the view functions for the e-commerce shopping application.
It handles all customer interactions including browsing products, managing the
shopping cart, and completing purchases.

The module also includes functionality to simulate various failure scenarios
for testing and demonstration purposes.
"""

import random
import time
import uuid

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods
from statustracker.models import StatusLog
from statustracker.views import log_status

from .models import Cart, CartItem, Category, Order, OrderItem, Product


def get_or_create_cart(customer_id):
    """
    Get or create a shopping cart for the customer.
    
    This helper function retrieves an existing cart for the customer or
    creates a new one if none exists. It also handles simulation of
    various failure scenarios for testing purposes.
    
    Args:
        customer_id (str): The unique identifier for the customer
        
    Returns:
        Cart: The customer's shopping cart object, or None if session failure
        
    Raises:
        Exception: If database connection failure is simulated
    """
    # Simulate session failure if requested
    if customer_id and customer_id.endswith('_session_fail'):
        return None
    
    # Simulate database connection error
    if customer_id and customer_id.endswith('_db_fail'):
        raise Exception("Simulated database connection error")
        
    cart, created = Cart.objects.get_or_create(customer_id=customer_id)
    return cart

def index(request):
    """
    Main shopping page view - Status Code: 101
    
    Displays the homepage of the shopping application with featured products
    and categories. This view also handles customer session initialization
    and various failure simulation scenarios.
    
    Args:
        request: The HTTP request object
        
    Returns:
        HttpResponse: Rendered index template with categories and featured products
        
    Failure Scenarios:
        - server: Returns a 500 Internal Server Error
        - session: Simulates corrupted session data
        - slow: Adds a 5-second delay to the response
        - query: Forces an invalid database query
    """
    # Simulate server error
    if request.GET.get('fail') == 'server':
        log_status(StatusLog.SELECT_SHOPPING_PAGE, 'unknown', False, "Server error on main page")
        return HttpResponse("Internal Server Error", status=500)
    
    # Initialize or retrieve customer session
    customer_id = request.session.get('customer_id')
    if not customer_id:
        customer_id = str(uuid.uuid4())
        request.session['customer_id'] = customer_id
        
    # Simulate session corruption
    if request.GET.get('fail') == 'session':
        customer_id = f"{customer_id}_session_fail"
        
    # Log the operation
    log_status(StatusLog.SELECT_SHOPPING_PAGE, customer_id, True, "User accessed the shopping page")
    
    # Simulate slow response
    if request.GET.get('fail') == 'slow':
        time.sleep(5)  # 5-second delay
    
    try:
        # Retrieve all product categories
        categories = Category.objects.all()
        
        # Simulate database query failure
        if request.GET.get('fail') == 'query':
            # Force a query error
            categories = Category.objects.filter(name__contains=None)
            
        # Get featured products for the homepage
        featured_products = Product.objects.all()[:6]  # Get some featured products
    except Exception as e:
        # Log and handle database errors
        log_status(StatusLog.SELECT_SHOPPING_PAGE, customer_id, False, f"Database error: {str(e)}")
        messages.error(request, "We're experiencing technical difficulties. Please try again later.")
        return HttpResponse("Database Error", status=500)
    
    # Render the homepage template
    return render(request, 'shoppingapp/index.html', {
        'categories': categories,
        'featured_products': featured_products
    })

def amazon_selection(request):
    """Select Amazon as the shopping platform - Status Code: 102"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Log the operation
    log_status(StatusLog.SELECT_AMAZON, customer_id, True, "User selected Amazon as the shopping platform")
    
    return redirect('category_list')

def category_list(request):
    """View all categories - Status Code: 103"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Log the operation
    log_status(StatusLog.SELECT_CATEGORY, customer_id, True, "User viewed categories")
    
    categories = Category.objects.all()
    return render(request, 'shoppingapp/category_list.html', {'categories': categories})

def product_list(request, category_id):
    """Browse products in a category - Status Code: 104"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    category = get_object_or_404(Category, id=category_id)
    
    # Log the operation
    log_status(StatusLog.BROWSE_ITEMS, customer_id, True, f"User browsed products in {category.name}")
    
    products = Product.objects.filter(category=category)
    return render(request, 'shoppingapp/product_list.html', {
        'category': category,
        'products': products
    })

def product_detail(request, product_id):
    """View product details - Status Code: 105"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Simulate product not found
    if request.GET.get('fail') == 'notfound':
        log_status(StatusLog.SELECT_ITEM, customer_id, False, f"Product not found (ID: {product_id})")
        messages.error(request, "The product you're looking for doesn't exist or has been removed.")
        return redirect('category_list')
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Simulate data corruption
        if request.GET.get('fail') == 'corrupt':
            log_status(StatusLog.SELECT_ITEM, customer_id, False, f"Product data corruption for {product.name}")
            messages.error(request, "This product information is currently unavailable due to data corruption.")
            return redirect('category_list')
            
        # Log the operation
        log_status(StatusLog.SELECT_ITEM, customer_id, True, f"User viewed {product.name}")
        
        # Simulate random error
        if request.GET.get('fail') == 'random' and random.random() < 0.5:  # 50% chance of failure
            log_status(StatusLog.SELECT_ITEM, customer_id, False, f"Random error viewing {product.name}")
            messages.error(request, "Something went wrong. Please try again.")
            return redirect('category_list')
            
        return render(request, 'shoppingapp/product_detail.html', {'product': product})
        
    except Exception as e:
        log_status(StatusLog.SELECT_ITEM, customer_id, False, f"Error retrieving product: {str(e)}")
        messages.error(request, "We couldn't retrieve this product. Please try again later.")
        return redirect('category_list')

@require_http_methods(["POST"])
def add_to_cart(request, product_id):
    """Add product to cart - Status Code: 106"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Simulate rate limiting
    if request.GET.get('fail') == 'ratelimit':
        log_status(StatusLog.ADD_TO_CART, customer_id, False, "Rate limit exceeded")
        messages.error(request, "You've made too many requests. Please try again later.")
        return redirect('product_detail', product_id=product_id)
    
    try:
        product = get_object_or_404(Product, id=product_id)
        
        # Simulate invalid input
        if request.GET.get('fail') == 'input':
            quantity = -1  # Force invalid quantity
        else:
            try:
                quantity = int(request.POST.get('quantity', 1))
            except ValueError:
                # Log failure - invalid quantity format
                log_status(StatusLog.ADD_TO_CART, customer_id, False, f"Failed to add {product.name} to cart - Invalid quantity format")
                messages.error(request, "Please enter a valid quantity")
                return redirect('product_detail', product_id=product_id)
        
        if quantity <= 0 or quantity > product.stock:
            # Log failure
            log_status(StatusLog.ADD_TO_CART, customer_id, False, f"Failed to add {product.name} to cart - Invalid quantity")
            messages.error(request, "Invalid quantity")
            return redirect('product_detail', product_id=product_id)
        
        # Simulate inventory system failure
        if request.GET.get('fail') == 'inventory':
            log_status(StatusLog.ADD_TO_CART, customer_id, False, f"Inventory system failure for {product.name}")
            messages.error(request, "Inventory system temporarily unavailable")
            return redirect('product_detail', product_id=product_id)
            
        try:
            cart = get_or_create_cart(customer_id)
            
            # Handle session failure
            if cart is None:
                log_status(StatusLog.ADD_TO_CART, customer_id, False, "Session error - couldn't retrieve cart")
                messages.error(request, "Your shopping session has expired. Please try again.")
                return redirect('index')
                
            # Check if product already in cart
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': quantity}
            )
            
            if not created:
                cart_item.quantity += quantity
                cart_item.save()
            
            # Simulate transaction failure
            if request.GET.get('fail') == 'transaction':
                raise ValidationError("Simulated transaction failure")
                
            # Log success
            log_status(StatusLog.ADD_TO_CART, customer_id, True, f"Added {quantity} x {product.name} to cart")
            
            messages.success(request, f"{product.name} added to your cart")
            return redirect('cart_view')
            
        except Exception as e:
            log_status(StatusLog.ADD_TO_CART, customer_id, False, f"Error adding to cart: {str(e)}")
            messages.error(request, "We couldn't add this item to your cart. Please try again later.")
            return redirect('product_detail', product_id=product_id)
            
    except Exception as e:
        log_status(StatusLog.ADD_TO_CART, customer_id, False, f"Error retrieving product: {str(e)}")
        messages.error(request, "We couldn't find this product. Please try again later.")
        return redirect('category_list')

def cart_view(request):
    """
    View shopping cart contents.
    
    Displays all items in the customer's shopping cart along with quantities,
    prices, and the total amount. This view handles both GET requests to display
    the cart and POST requests to clear the cart.
    
    Args:
        request: The HTTP request object
        
    Returns:
        HttpResponse: Rendered cart template with cart items and total
    """
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    cart = get_or_create_cart(customer_id)
    cart_items = CartItem.objects.filter(cart=cart)
    
    # Calculate total price of all items in cart
    total = sum(item.product.price * item.quantity for item in cart_items)
    
    return render(request, 'shoppingapp/cart.html', {
        'cart_items': cart_items,
        'total': total
    })
    
@require_http_methods(["POST"])
def clear_cart(request):
    """
    Clear all items from the shopping cart.
    
    Removes all items from the customer's shopping cart and redirects
    back to the empty cart view with a confirmation message.
    
    Args:
        request: The HTTP request object
        
    Returns:
        HttpResponse: Redirect to cart view with success message
    """
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    try:
        # Get the customer's cart
        cart = get_or_create_cart(customer_id)
        
        # Handle session failure
        if cart is None:
            messages.error(request, "Your shopping session has expired. Please try again.")
            return redirect('index')
            
        # Delete all cart items
        item_count = CartItem.objects.filter(cart=cart).count()
        CartItem.objects.filter(cart=cart).delete()
        
        # Log the operation (using ADD_TO_CART code since there's no specific clear cart code)
        log_status(
            StatusLog.ADD_TO_CART, 
            customer_id, 
            True, 
            f"Cleared {item_count} items from cart"
        )
        
        messages.success(request, "Your cart has been cleared.")
    except Exception as e:
        # Log failure
        log_status(
            StatusLog.ADD_TO_CART, 
            customer_id, 
            False, 
            f"Failed to clear cart: {str(e)}"
        )
        messages.error(request, "We couldn't clear your cart. Please try again later.")
    
    return redirect('cart_view')

@require_http_methods(["POST"])
def checkout(request):
    """Complete purchase - Status Code: 107"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Simulate payment processing failure
    if request.GET.get('fail') == 'payment':
        failure_type = request.GET.get('type', 'declined')
        
        error_message = "Payment processing failed"
        if failure_type == 'timeout':
            error_message = "Payment gateway timed out. Please try again."
        elif failure_type == 'declined':
            error_message = "Payment was declined. Please use a different payment method."
        elif failure_type == 'insufficient_funds':
            error_message = "Insufficient funds in account."
        
        log_status(StatusLog.BUY_ITEM, customer_id, False, f"Payment failure: {failure_type}")
        messages.error(request, error_message)
        return redirect('cart_view')
    
    # Simulate network issues
    if request.GET.get('fail') == 'network':
        issue_type = request.GET.get('type', 'slow')
        
        if issue_type == 'slow':
            # Simulate slow response
            time.sleep(5)
        elif issue_type == 'timeout':
            # Simulate timeout
            time.sleep(10)
            log_status(StatusLog.BUY_ITEM, customer_id, False, "Network timeout during checkout")
            messages.error(request, "The request timed out. Please try again.")
            return redirect('cart_view')
    
    try:
        cart = get_or_create_cart(customer_id)
        
        # Handle session failure
        if cart is None:
            log_status(StatusLog.BUY_ITEM, customer_id, False, "Session error - couldn't retrieve cart")
            messages.error(request, "Your shopping session has expired. Please try again.")
            return redirect('index')
            
        cart_items = CartItem.objects.filter(cart=cart)
        
        if not cart_items:
            # Log failure
            log_status(StatusLog.BUY_ITEM, customer_id, False, "Checkout failed - Cart is empty")
            messages.error(request, "Your cart is empty")
            return redirect('cart_view')
        
        # Calculate total
        total = sum(item.product.price * item.quantity for item in cart_items)
        
        # Simulate third-party service failure
        if request.GET.get('fail') == 'service':
            service_type = request.GET.get('type', 'shipping')
            
            error_message = "Service temporarily unavailable"
            if service_type == 'shipping':
                error_message = "Shipping calculation service unavailable. Please try again later."
            elif service_type == 'tax':
                error_message = "Tax calculation service unavailable. Please try again later."
            
            log_status(StatusLog.BUY_ITEM, customer_id, False, f"{service_type.capitalize()} service failure")
            messages.error(request, error_message)
            return redirect('cart_view')
        
        # Simulate database failure
        if request.GET.get('fail') == 'database':
            log_status(StatusLog.BUY_ITEM, customer_id, False, "Database connection error during checkout")
            messages.error(request, "We're experiencing technical difficulties. Please try again later.")
            return redirect('cart_view')
        
        try:
            # Create order
            order = Order.objects.create(
                customer_id=customer_id,
                total_amount=total
            )
            
            # Simulate partial order failure
            partial_failure = request.GET.get('fail') == 'partial'
            processed_items = 0
            
            # Create order items
            for cart_item in cart_items:
                # If simulating partial failure, fail after processing half the items
                if partial_failure and processed_items >= len(cart_items) // 2:
                    raise Exception("Simulated partial order failure")
                
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Update product stock
                product = cart_item.product
                
                # Simulate out-of-stock condition
                if request.GET.get('fail') == 'stock' and product.stock < cart_item.quantity:
                    log_status(StatusLog.BUY_ITEM, customer_id, False, f"Out of stock: {product.name}")
                    messages.error(request, f"{product.name} is out of stock. Please remove it from your cart.")
                    return redirect('cart_view')
                
                product.stock -= cart_item.quantity
                product.save()
                processed_items += 1
            
            # Clear cart
            cart_items.delete()
            
            # Log success
            log_status(StatusLog.BUY_ITEM, customer_id, True, f"Completed purchase - Order #{order.id}")
            
            messages.success(request, "Your order has been placed successfully!")
            return redirect('order_confirmation', order_id=order.id)
            
        except Exception as e:
            # Log order processing failure
            log_status(StatusLog.BUY_ITEM, customer_id, False, f"Order processing error: {str(e)}")
            messages.error(request, "We couldn't process your order. Please try again later.")
            return redirect('cart_view')
            
    except Exception as e:
        # Log general checkout failure
        log_status(StatusLog.BUY_ITEM, customer_id, False, f"Checkout error: {str(e)}")
        messages.error(request, "An error occurred during checkout. Please try again later.")
        return redirect('cart_view')

def order_confirmation(request, order_id):
    """Order confirmation page"""
    customer_id = request.session.get('customer_id', str(uuid.uuid4()))
    
    # Simulate order not found
    if request.GET.get('fail') == 'notfound':
        messages.error(request, "Order not found. Please contact customer support.")
        return redirect('index')
    
    try:
        order = get_object_or_404(Order, id=order_id, customer_id=customer_id)
        
        # Simulate data corruption
        if request.GET.get('fail') == 'corrupt':
            messages.error(request, "Order information is corrupted. Please contact customer support.")
            return redirect('index')
            
        order_items = OrderItem.objects.filter(order=order)
        
        return render(request, 'shoppingapp/order_confirmation.html', {
            'order': order,
            'order_items': order_items
        })
        
    except Exception as e:
        messages.error(request, "We couldn't retrieve your order information. Please try again later.")
        return redirect('index')

def trigger_failure(request):
    """View to demonstrate different failure scenarios"""
    failure_type = request.GET.get('type', 'none')
    
    failure_descriptions = {
        'server': "Server error - Returns a 500 Internal Server Error",
        'session': "Session corruption - Simulates corrupted session data",
        'slow': "Slow response - Adds a 5-second delay to the response",
        'query': "Database query failure - Forces an invalid database query",
        'notfound': "Not found error - Simulates a resource not found",
        'corrupt': "Data corruption - Simulates corrupted data",
        'random': "Random failure - 50% chance of failure",
        'ratelimit': "Rate limiting - Simulates rate limit exceeded",
        'input': "Invalid input - Forces invalid input data",
        'inventory': "Inventory system failure - Simulates inventory system unavailable",
        'transaction': "Transaction failure - Simulates a database transaction failure",
        'payment': "Payment processing failure - Simulates payment gateway issues",
        'network': "Network issues - Simulates network connectivity problems",
        'service': "Third-party service failure - Simulates external service unavailability",
        'database': "Database connection error - Simulates database connectivity issues",
        'partial': "Partial order failure - Processes only part of an order",
        'stock': "Out of stock - Simulates out of stock condition during checkout"
    }
    
    return render(request, 'shoppingapp/failure_guide.html', {
        'failure_type': failure_type,
        'failure_descriptions': failure_descriptions
    })