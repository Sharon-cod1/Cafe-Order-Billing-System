from django.db import models
from django.contrib.auth.models import User

class Staff(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pin_code = models.CharField(max_length=4)  # For quick login (e.g., "1234")
    is_active = models.BooleanField(default=True)

class Shift(models.Model):
    staff = models.ForeignKey(Staff, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

class MenuItem(models.Model):
    CATEGORIES = [
        ('CHICKEN', 'Chicken Items'),
        ('SNACKS', 'Snacks'),
        ('DRINKS', 'Drinks'),
        ('DESSERTS', 'Desserts'),
        ('OTHER', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.CharField(max_length=10, choices=CATEGORIES)
    available = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    table_number = models.IntegerField()
    order_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    total_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    staff = models.ForeignKey(Staff, null=True, on_delete=models.SET_NULL)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_status = models.CharField(max_length=20,choices=[('pending', 'Pending'), ('paid', 'Paid'), ('failed', 'Failed')],default='pending')

    
    def __str__(self):
        return f"Order #{self.id} - Table {self.table_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name} for Order #{self.order.id}"
    
