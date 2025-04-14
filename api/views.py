from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import models
from rest_framework.pagination import PageNumberPagination
from .models import Product, Category, InventoryTransaction
from .serializers import (
    ProductListSerializer, ProductDetailSerializer,
    CategorySerializer,
    InventoryTransactionListSerializer, InventoryTransactionDetailSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """API endpoint للفئات"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """الحصول على جميع المنتجات في فئة معينة"""
        category = self.get_object()
        products = category.products.all()
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """API endpoint للمنتجات"""
    queryset = Product.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'current_quantity']
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['name', 'price', 'current_quantity', 'created_at']
    pagination_class = StandardResultsSetPagination  
    
    def get_queryset(self):
        """Optimize queries to avoid the N+1 problem"""
        if self.action == 'list' or self.action == 'low_stock' or self.action == 'out_of_stock':
            # Use select_related to preload category data when displaying product listings.
            return Product.objects.select_related('category').all()
        elif self.action == 'retrieve':
            # When viewing details of a single product, you may need additional data.
            return Product.objects.select_related('category').all()
        elif self.action == 'transactions':
            # When viewing product transactions, you may need to preload the transactions as well.
            return Product.objects.prefetch_related('transactions__user').all()
        return Product.objects.all()
    
    def get_serializer_class(self):
        """Determine the serializer class based on the request type."""
        if self.action == 'list':
            return ProductListSerializer
        return ProductDetailSerializer
    
    def get_serializer_context(self):
        """
        Add request to serializer context to build absolute URLs for images
        """
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context
    
    @action(detail=True, methods=['get'], url_path='transactions')
    def transactions(self, request, pk=None):
        """Get all inventory transactions for a specific product"""
        product = self.get_object()
        transactions = InventoryTransaction.objects.filter(product=product).select_related('product')
        serializer = InventoryTransactionListSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='low-stock')
    def low_stock(self, request):
        """Get products that need to be reordered"""
        products = Product.objects.filter(current_quantity__lte=models.F('min_quantity'))
        page = self.paginate_queryset(products)
        
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='out-of-stock')
    def out_of_stock(self, request):
        """Get out of stock products"""
        products = Product.objects.filter(current_quantity=0)
        page = self.paginate_queryset(products)
        
        if page is not None:
            serializer = ProductListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(products, many=True)
        return Response(serializer.data)


class InventoryTransactionViewSet(viewsets.ModelViewSet):
    """API endpoint for inventory transactions"""
    queryset = InventoryTransaction.objects.all().order_by('-transaction_date')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['product', 'transaction_type', 'user', 'transaction_date']
    search_fields = ['product__name', 'reason', 'note']
    ordering_fields = ['transaction_date', 'quantity']
    
    def get_serializer_class(self):
        """Determine the serializer class based on the request type"""
        if self.action == 'list':
            return InventoryTransactionListSerializer
        return InventoryTransactionDetailSerializer
    
    def perform_create(self, serializer):
        """Set the current user when creating a new transaction"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get the latest stock transactions"""
        transactions = InventoryTransaction.objects.all().order_by('-transaction_date')[:10]
        serializer = InventoryTransactionListSerializer(transactions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get a summary of inventory transactions"""
        from django.db.models import Sum, Count
        
        # Total quantities by transaction type
        total_in = InventoryTransaction.objects.filter(transaction_type='IN').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        total_out = InventoryTransaction.objects.filter(transaction_type='OUT').aggregate(
            total=Sum('quantity')
        )['total'] or 0
        
        # Number of transactions by type
        transactions_count = InventoryTransaction.objects.values('transaction_type').annotate(
            count=Count('id')
        )
        
        # Convert results to a dictionary for ease of use
        counts_by_type = {item['transaction_type']: item['count'] for item in transactions_count}
        
        return Response({
            'total_in': total_in,
            'total_out': total_out,
            'net_change': total_in - total_out,
            'transactions_count': counts_by_type
        })
