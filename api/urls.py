from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# إنشاء راوتر للـ API
router = DefaultRouter()
router.register(r'products', views.ProductViewSet)
router.register(r'categories', views.CategoryViewSet)
router.register(r'transactions', views.InventoryTransactionViewSet)

# تعريف أنماط URL
urlpatterns = [
    # تضمين مسارات API الأساسية من الراوتر
    path('api/', include(router.urls)),
    
    # مسارات إضافية خاصة
    # للمنتجات التي على وشك ان تنفذ
    path('api/products/low-stock/', views.ProductViewSet.as_view({'get': 'low_stock'}), name='low-stock-products'),
    # المنتجات التي نفذت كميتها
    path('api/products/out-of-stock/', views.ProductViewSet.as_view({'get': 'out_of_stock'}), name='out-of-stock-products'),
    # آخر معاملات Transaction
    path('api/transactions/latest/', views.InventoryTransactionViewSet.as_view({'get': 'latest'}), name='latest-transactions'),
    # ملخص معاملات Transaction
    path('api/transactions/summary/', views.InventoryTransactionViewSet.as_view({'get': 'summary'}), name='transactions-summary'),
    # استخدم أيضا products/<id>/transactions للحصول على جميع المعاملات لمنتج معين
    
]
