from rest_framework import serializers
from .models import Product, Category, InventoryTransaction
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for brief user data"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at', 'updated_at', 'products_count']
    
    def get_products_count(self, obj):
        """Count the number of products in this category"""
        return obj.products.count()


class ProductListSerializer(serializers.ModelSerializer):
    """Serializer for Products (for product lists)"""
    category_name = serializers.ReadOnlyField(source='category.name')
    stock_status = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = ['id', 'name', 'sku', 'price', 'current_quantity', 'category_name', 'stock_status', 'image_url']
    
    def get_stock_status(self, obj):
        """Determine stock status"""
        if obj.current_quantity <= 0:
            return "out_of_stock"
        elif obj.current_quantity <= obj.min_quantity:
            return "low_stock"
        else:
            return "in_stock"
    
    def get_image_url(self, obj):
        """Get complete image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed Product Serializer (for product detail page)"""
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), 
        source='category',
        write_only=True,
        required=False,
        allow_null=True
    )
    stock_status = serializers.SerializerMethodField()
    profit_margin = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'sku', 'price', 'cost_price', 
            'current_quantity', 'min_quantity', 'category', 'category_id',
            'image','image_url', 'created_at', 'updated_at', 'stock_status',
            'profit_margin'
        ]
    
    def get_stock_status(self, obj):
        """Determine inventory status"""
        if obj.current_quantity <= 0:
            return "out_of_stock"
        elif obj.current_quantity <= obj.min_quantity:
            return "low_stock"
        else:
            return "in_stock"
    
    def get_profit_margin(self, obj):
        """Profit margin calculation"""
        if obj.cost_price > 0:
            margin = ((obj.price - obj.cost_price) / obj.price) * 100
            return round(margin, 2)
        return None
    
    def get_image_url(self, obj):
        """Get complete image URL"""
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class InventoryTransactionListSerializer(serializers.ModelSerializer):
    """Serializer is short for transactions."""
    product_name = serializers.ReadOnlyField(source='product.name')
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    user_name = serializers.SerializerMethodField()
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product_name', 'transaction_type', 'transaction_type_display',
            'quantity', 'transaction_date', 'user_name'
        ]
    
    def get_user_name(self, obj):
        if obj.user:
            return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
        return None


class InventoryTransactionDetailSerializer(serializers.ModelSerializer):
    """Detailed Transaction Serializer"""
    product = ProductListSerializer(read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )
    user = UserSerializer(read_only=True)
    transaction_type_display = serializers.ReadOnlyField(source='get_transaction_type_display')
    
    class Meta:
        model = InventoryTransaction
        fields = [
            'id', 'product', 'product_id', 'transaction_type', 'transaction_type_display',
            'quantity', 'reason', 'user', 'transaction_date', 'note',
            'previous_quantity'
        ]
    
    def validate_quantity(self, value):
        """Quantity validation"""
        if value <= 0:
            raise serializers.ValidationError("The quantity must be greater than zero.")
        return value
    
    def validate(self, data):
        """Verify the complete transaction"""
        if data.get('transaction_type') == 'OUT':
            product = data.get('product')
            quantity = data.get('quantity')
            if product.current_quantity < quantity:
                raise serializers.ValidationError({
                    "quantity": f"Insufficient quantity. Available: {product.current_quantity}, Required: {quantity}"
                })
        return data
