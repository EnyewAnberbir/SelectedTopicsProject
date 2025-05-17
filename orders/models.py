from django.db import models
from django.utils.crypto import get_random_string
from users.models import User, Address
from products.models import Product


class Order(models.Model):
    """Order model."""
    
    ORDER_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True, editable=False)
    shipping_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name='shipping_orders'
    )
    billing_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, related_name='billing_orders'
    )
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, null=True, blank=True)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('-created_at',)
    
    def __str__(self):
        return f"Order #{self.order_number}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)
    
    def _generate_order_number(self):
        """Generate a unique order number."""
        return f"ORD-{get_random_string(16).upper()}"
    
    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    """Order item model."""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=255)  # Store the name in case the product is deleted
    product_price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at the time of purchase
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.product_name} ({self.quantity}) in Order #{self.order.order_number}"
    
    def save(self, *args, **kwargs):
        # Calculate total price if not already set
        if not self.total_price:
            self.total_price = self.product_price * self.quantity
        super().save(*args, **kwargs) 