from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from . import views

# Create a router for the API
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'transactions', views.InventoryTransactionViewSet)

# Define URL patterns
urlpatterns = [
    # Include basic API routes from the router
    path('api/', include(router.urls)),
    
    # Special additional URLS
    # For products that are about to run out
    path('api/products/low-stock/', views.ProductViewSet.as_view({'get': 'low_stock'}), name='low-stock-products'),
    # Out of stock products
    path('api/products/out-of-stock/', views.ProductViewSet.as_view({'get': 'out_of_stock'}), name='out-of-stock-products'),
    # Latest Transaction
    path('api/transactions/latest/', views.InventoryTransactionViewSet.as_view({'get': 'latest'}), name='latest-transactions'),
    # Transaction summary
    path('api/transactions/summary/', views.InventoryTransactionViewSet.as_view({'get': 'summary'}), name='transactions-summary'),
    # Also use products/<id>/transactions to get all transactions for a specific product.    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
