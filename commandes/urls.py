# commandes/urls.py
from django.urls import path
from . import views

app_name = 'commandes'

urlpatterns = [
    path('panier/',                     views.cart_view,        name='cart'),
    path('ajouter/<int:product_id>/',   views.add_to_cart,      name='add_to_cart'),
    path('supprimer/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/',                   views.checkout_view,    name='checkout'),
    path('confirmation/<int:pk>/',      views.order_success,    name='order_success'),
    path('suivi/',                      views.suivi_view,       name='suivi'),
    path('preuve-paiement/',            views.upload_preuve,    name='upload_preuve'),
    path('update/<int:product_id>/',    views.update_cart,      name='update_cart'),
    path('dashboard/',                  views.dashboard,        name='dashboard'),
]
