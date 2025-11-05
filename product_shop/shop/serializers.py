from rest_framework import serializers
from .models import Category, SubCategory, Product, ProductImage, Cart, CartItem


class SubCategorySerializer(serializers.ModelSerializer):
    """Сериализатор подкатегории"""
    
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'slug', 'image']
        read_only_fields = ['id']


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории с подкатегориями"""
    subcategories = SubCategorySerializer(many=True, read_only=True)
    image = serializers.ImageField(required=False)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'subcategories']
        read_only_fields = ['id']


class ProductImageSerializer(serializers.ModelSerializer):
    """Сериализатор изображений продукта"""
    
    class Meta:
        model = ProductImage
        fields = ['image_small', 'image_medium', 'image_large']
        read_only_fields = ['id']


class ProductSerializer(serializers.ModelSerializer):
    """Сериализатор продукта для списка"""
    category = serializers.CharField(source='category.name', read_only=True)
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'subcategory', 
            'price', 'description', 'images', 'is_available'
        ]
        read_only_fields = ['id', 'category', 'subcategory']
    
    def get_images(self, obj):
        """Получить список изображений продукта"""
        images = obj.images.all()
        if not images:
            return []
        return [ProductImageSerializer(img).data for img in images]


class ProductDetailSerializer(serializers.ModelSerializer):
    """Детальный сериализатор продукта"""
    category = serializers.CharField(source='category.name', read_only=True)
    subcategory = serializers.CharField(source='subcategory.name', read_only=True)
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category', 'subcategory', 
            'price', 'description', 'images', 'is_available'
        ]
        read_only_fields = ['id']
    
    def get_images(self, obj):
        """Получить список изображений продукта"""
        images = obj.images.all()
        if not images:
            return []
        return [ProductImageSerializer(img).data for img in images]


class CartItemSerializer(serializers.ModelSerializer):
    """Сериализатор элемента корзины"""
    product = ProductSerializer(read_only=True)
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']
        read_only_fields = ['id', 'total_price']


class CartItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления элемента корзины"""
    product_id = serializers.IntegerField(write_only=True, required=False)
    
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity']
    
    def create(self, validated_data):
        cart = self.context['cart']
        product_id = validated_data.pop('product_id')
        quantity = validated_data.pop('quantity', 1)
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Продукт не найден")
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
    
    def update(self, instance, validated_data):
        """Обновление количества продукта в корзине"""
        # При update можно менять только quantity
        validated_data.pop('product_id', None)  # Игнорируем product_id при update
        
        quantity = validated_data.get('quantity', instance.quantity)
        if quantity <= 0:
            instance.delete()
            return instance
        
        instance.quantity = quantity
        instance.save()
        return instance


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины"""
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_items', 'total_price']
        read_only_fields = ['id', 'total_items', 'total_price']


