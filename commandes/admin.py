# commandes/admin.py
from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['produit', 'quantite', 'prix_unitaire', 'sous_total']

    def sous_total(self, obj):
        return f'{obj.sous_total} DA'
    sous_total.short_description = 'Sous-total'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display  = ['id', 'nom_client', 'telephone', 'type_livraison', 'wilaya', 'statut', 'total', 'date_commande']
    list_filter   = ['statut', 'type_livraison', 'wilaya', 'date_commande']
    list_editable = ['statut']
    search_fields = ['nom_client', 'telephone']
    readonly_fields = ['date_commande', 'total']
    inlines = [OrderItemInline]
    fieldsets = (
        ('Client', {'fields': ('nom_client', 'telephone')}),
        ('Livraison', {'fields': ('type_livraison', 'wilaya', 'commune', 'adresse')}),
        ('Paiement & Statut', {'fields': ('mode_paiement', 'statut', 'total')}),
        ('Notes', {'fields': ('notes', 'date_commande')}),
    )
