from django.contrib import admin
from django.contrib.auth.models import Group, User
from .models import Category, SubCategory, Product, ProductImage, Cart, CartItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'category__name']
    list_filter = ['category', 'created_at']


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'subcategory', 'price', 'is_available', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']
    list_filter = ['is_available', 'subcategory__category', 'subcategory', 'created_at']
    inlines = [ProductImageInline]


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at']
    readonly_fields = ['total_items', 'total_price']
    search_fields = ['user__username', 'user__email']
    inlines = [CartItemInline]
    
    def total_items(self, obj):
        return obj.total_items
    total_items.short_description = 'Количество товаров'
    
    def total_price(self, obj):
        return f"{obj.total_price:.2f} руб."
    total_price.short_description = 'Общая стоимость'


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['product', 'cart', 'quantity', 'total_price']
    readonly_fields = ['total_price']
    search_fields = ['product__name']
    
    def total_price(self, obj):
        return f"{obj.total_price:.2f} руб."
    total_price.short_description = 'Общая стоимость'

# Скрыть раздел Groups из админки
from django.contrib.admin.sites import NotRegistered
try:
    admin.site.unregister(Group)
except NotRegistered:
    pass

# Изменить название модели User в админке
admin.site.index_title = "Администрирование магазина"
admin.site.site_title = "Панель управления магазином"
admin.site.site_header = "Администрирование магазина"

# Кастомизация модели User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class CustomUserAdmin(BaseUserAdmin):
    pass

# Перерегистрируем модель User с русским названием
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# Изменяем verbose_name для User в админке
User._meta.verbose_name = "Пользователь"
User._meta.verbose_name_plural = "Пользователи"
