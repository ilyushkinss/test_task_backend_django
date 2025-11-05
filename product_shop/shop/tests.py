from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from .models import Category, SubCategory, Product, Cart, CartItem


class CategoryAPITestCase(APITestCase):
    """Тесты для API категорий"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Тестовая подкатегория',
            slug='test-subcategory'
        )
        self.client = APIClient()
    
    def test_get_categories_list(self):
        """Тест получения списка категорий (GET)"""
        url = '/api/v1/categories/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Тестовая категория')
    
    def test_get_category_detail(self):
        """Тест получения детальной информации о категории (GET)"""
        url = f'/api/v1/categories/{self.category.slug}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовая категория')
        self.assertIn('subcategories', response.data)


class ProductAPITestCase(APITestCase):
    """Тесты для API продуктов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Тестовая подкатегория',
            slug='test-subcategory'
        )
        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name='Тестовый продукт',
            slug='test-product',
            price=99.99
        )
        self.client = APIClient()
    
    def test_get_products_list(self):
        """Тест получения списка продуктов (GET)"""
        url = '/api/v1/products/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name'], 'Тестовый продукт')
        self.assertEqual(float(response.data['results'][0]['price']), 99.99)
    
    def test_get_product_detail(self):
        """Тест получения детальной информации о продукте (GET)"""
        url = f'/api/v1/products/{self.product.slug}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Тестовый продукт')
        self.assertIn('category', response.data)
        self.assertIn('subcategory', response.data)


class CartAPITestCase(APITestCase):
    """Тесты для API корзины"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.category = Category.objects.create(
            name='Тестовая категория',
            slug='test-category'
        )
        self.subcategory = SubCategory.objects.create(
            category=self.category,
            name='Тестовая подкатегория',
            slug='test-subcategory'
        )
        self.product = Product.objects.create(
            subcategory=self.subcategory,
            name='Тестовый продукт',
            slug='test-product',
            price=99.99
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.cart = Cart.objects.create(user=self.user)
    
    def test_get_cart(self):
        """Тест получения корзины (GET)"""
        url = '/api/v1/cart/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('items', response.data)
        self.assertIn('total_items', response.data)
        self.assertIn('total_price', response.data)
    
    def test_add_item_to_cart(self):
        """Тест добавления продукта в корзину (POST)"""
        url = '/api/v1/cart/items/'
        data = {
            'product_id': self.product.id,
            'quantity': 2
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CartItem.objects.count(), 1)
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.quantity, 2)
    
    def test_update_item_in_cart(self):
        """Тест обновления количества продукта в корзине"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        url = f'/api/v1/cart/items/{cart_item.id}/'
        data = {'quantity': 5}
        response = self.client.patch(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
    
    def test_delete_item_from_cart(self):
        """Тест удаления продукта из корзины"""
        cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        url = f'/api/v1/cart/items/{cart_item.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CartItem.objects.count(), 0)
    
    def test_clear_cart(self):
        """Тест очистки корзины"""
        CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1
        )
        url = f'/api/v1/cart/{self.cart.id}/'
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CartItem.objects.count(), 0)


class AuthAPITestCase(APITestCase):
    """Тесты для API авторизации"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.client = APIClient()
    
    def test_register_user(self):
        """Тест регистрации нового пользователя (POST)"""
        url = '/api/v1/auth/register/'
        data = {
            'username': 'newuser',
            'password': 'newpass123',
            'email': 'newuser@test.com'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_obtain_token(self):
        """Тест получения токена (POST)"""
        User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        url = '/api/v1/auth/token/'
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
