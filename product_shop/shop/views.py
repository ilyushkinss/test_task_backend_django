from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from django.db import transaction
from .models import Category, SubCategory, Product, Cart, CartItem
from .serializers import (
    CategorySerializer, ProductSerializer, ProductDetailSerializer,
    CartSerializer, CartItemSerializer, CartItemCreateUpdateSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для категорий"""
    queryset = Category.objects.prefetch_related('subcategories').all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для продуктов"""
    queryset = Product.objects.select_related('subcategory', 'subcategory__category').prefetch_related('images').all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        return ProductSerializer
    
    def get_queryset(self):
        """Фильтрация по подкатегории и категории"""
        queryset = super().get_queryset()
        subcategory_slug = self.request.query_params.get('subcategory')
        category_slug = self.request.query_params.get('category')
        
        if subcategory_slug:
            queryset = queryset.filter(subcategory__slug=subcategory_slug)
        elif category_slug:
            queryset = queryset.filter(subcategory__category__slug=category_slug)
        
        return queryset


class CartViewSet(viewsets.ModelViewSet):
    """
    ViewSet для корзины
    
    GET /api/v1/cart/ - просмотр корзины
    DELETE /api/v1/cart/{pk}/ - очистка корзины (pk игнорируется, очищается корзина текущего пользователя)
    """
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'delete']
    
    def get_queryset(self):
        """Пользователь видит только свою корзину"""
        return Cart.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        """Получить корзину пользователя с подсчетом количества и суммы"""
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(cart)
        return Response(serializer.data)
    
    def get_object(self):
        """Получить корзину пользователя"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart
    
    def destroy(self, request, *args, **kwargs):
        """Полная очистка корзины"""
        cart = self.get_object()
        cart.items.all().delete()
        return Response({'message': 'Корзина очищена'}, status=status.HTTP_200_OK)


class CartItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet для элементов корзины
    
    POST /api/v1/cart/items/ - добавление продукта в корзину
    PATCH /api/v1/cart/items/{id}/ - изменение количества продукта
    DELETE /api/v1/cart/items/{id}/ - удаление продукта из корзины
    """
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['post', 'patch', 'delete']
    
    def get_queryset(self):
        """Получить элементы корзины текущего пользователя"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CartItemCreateUpdateSerializer
        elif self.action in ['update', 'partial_update']:
            return CartItemCreateUpdateSerializer
        return CartItemSerializer
    
    def perform_create(self, serializer):
        """Добавление продукта в корзину"""
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        serializer.save(cart=cart)
    
    def perform_update(self, serializer):
        """Обновление количества продукта"""
        serializer.save()
    
    def get_serializer_context(self):
        """Передать корзину в контекст сериализатора"""
        context = super().get_serializer_context()
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        context['cart'] = cart
        return context
