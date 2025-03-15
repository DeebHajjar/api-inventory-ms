from django.contrib import admin
from .models import Category, Product, InventoryTransaction

admin.site.register(Category)
admin.site.register(Product)
admin.site.register(InventoryTransaction)
