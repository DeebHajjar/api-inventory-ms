from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    current_quantity = models.PositiveIntegerField(default=0)
    min_quantity = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, blank=True, null=True, related_name='products')
    # Change from URLField to ImageField
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.sku})"
    
    def is_low_stock(self):
        """Check if product needs to be reordered"""
        return self.current_quantity <= self.min_quantity
    
    class Meta:
        ordering = ['name']


class InventoryTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
    )
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=3, choices=TRANSACTION_TYPES)
    quantity = models.IntegerField()
    reason = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions')
    transaction_date = models.DateTimeField(default=timezone.now)
    note = models.TextField(blank=True, null=True)
    previous_quantity = models.PositiveIntegerField(default=0)  # To record the quantity before the operation
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.product.name} - {self.quantity}"
    
    def save(self, *args, **kwargs):
        # Store the product's current quantity before making changes
        if not self.id:  # Only when creating a new transaction
            self.previous_quantity = self.product.current_quantity
            
        # Update product quantity when new inventory transaction is added
        if self.transaction_type == 'IN':
            self.product.current_quantity += self.quantity
        elif self.transaction_type == 'OUT':
            self.product.current_quantity -= self.quantity
        elif self.transaction_type == 'ADJ':
            self.product.current_quantity += self.quantity  # The quantity may be negative for downward adjustment.
        
        self.product.save()
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-transaction_date']
