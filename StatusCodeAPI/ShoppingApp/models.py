"""
Shopping Application Data Models

This module defines the data models for the e-commerce shopping application.
It includes models for products, categories, shopping carts, and orders.
"""

from django.db import models


class Category(models.Model):
    """
    Product category model.
    
    Categories are used to organize products into logical groups.
    Each product belongs to exactly one category.
    """
    name = models.CharField(max_length=100, help_text="Category name")
    description = models.TextField(blank=True, null=True, help_text="Optional category description")
    
    def __str__(self):
        """String representation of the category"""
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    """
    Product model representing items available for purchase.
    
    Each product belongs to a category and has details such as name,
    description, price, and current stock level.
    """
    name = models.CharField(max_length=200, help_text="Product name")
    description = models.TextField(help_text="Detailed product description")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        help_text="Product price in dollars"
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name='products',
        help_text="Category this product belongs to"
    )
    image_url = models.URLField(
        blank=True, 
        null=True, 
        help_text="URL to product image"
    )
    stock = models.PositiveIntegerField(
        default=0, 
        help_text="Current quantity available for purchase"
    )
    
    def __str__(self):
        """String representation of the product"""
        return self.name
    
    def is_in_stock(self):
        """Check if the product is currently in stock"""
        return self.stock > 0


class Cart(models.Model):
    """
    Shopping cart model.
    
    Each customer has one cart that can contain multiple cart items.
    Carts are identified by a unique customer ID.
    """
    customer_id = models.CharField(
        max_length=100, 
        help_text="Unique identifier for the customer"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text="When the cart was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text="When the cart was last updated"
    )
    
    def __str__(self):
        """String representation of the cart"""
        return f"Cart for {self.customer_id}"
    
    def get_total(self):
        """Calculate the total price of all items in the cart"""
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    """
    Shopping cart item model.
    
    Represents a product in a customer's shopping cart with a specified quantity.
    """
    cart = models.ForeignKey(
        Cart, 
        on_delete=models.CASCADE, 
        related_name='items',
        help_text="Cart this item belongs to"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        help_text="Product added to the cart"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of the product"
    )
    
    def __str__(self):
        """String representation of the cart item"""
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        """Calculate the total price for this cart item (quantity * price)"""
        return self.quantity * self.product.price


class Order(models.Model):
    """
    Customer order model.
    
    Represents a completed purchase with order status tracking.
    Each order contains one or more order items.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    customer_id = models.CharField(
        max_length=100,
        help_text="Unique identifier for the customer"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='pending',
        help_text="Current status of the order"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the order was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the order was last updated"
    )
    total_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Total order amount in dollars"
    )
    
    def __str__(self):
        """String representation of the order"""
        return f"Order {self.id} - {self.customer_id}"
    
    def get_status_display_name(self):
        """Get the human-readable status name"""
        return dict(self.STATUS_CHOICES).get(self.status, "Unknown")


class OrderItem(models.Model):
    """
    Order item model.
    
    Represents a product in a customer's order with quantity and price.
    The price is stored separately from the product price to maintain
    historical record of the price at the time of purchase.
    """
    order = models.ForeignKey(
        Order, 
        on_delete=models.CASCADE, 
        related_name='items',
        help_text="Order this item belongs to"
    )
    product = models.ForeignKey(
        Product, 
        on_delete=models.CASCADE,
        help_text="Product purchased"
    )
    quantity = models.PositiveIntegerField(
        default=1,
        help_text="Quantity of the product purchased"
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Price of the product at time of purchase"
    )
    
    def __str__(self):
        """String representation of the order item"""
        return f"{self.quantity} x {self.product.name}"
    
    @property
    def total_price(self):
        """Calculate the total price for this order item (quantity * price)"""
        return self.quantity * self.price