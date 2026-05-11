from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('nom',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['titre', 'categorie', 'prix_regulier', 'prix_vente', 'stock_quantite']
    list_editable = ['prix_regulier', 'prix_vente', 'stock_quantite']
    list_filter = ['categorie']
    prepopulated_fields = {'slug': ('titre',)}
