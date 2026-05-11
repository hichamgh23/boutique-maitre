# catalogue/urls.py
from django.urls import path
from . import views

app_name = 'catalogue'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('boutique/', views.boutique_view, name='boutique'),
    path('produit/<slug:slug>/', views.product_detail, name='product_detail'),
    path('contact/',           views.contact_view,     name='contact'),
    path('comment-ca-marche/', views.comment_ca_marche, name='comment_ca_marche'),
    path('api/search/',                  views.search_api,               name='search_api'),
    path('politique-confidentialite/',   views.politique_confidentialite, name='politique_confidentialite'),
    path('cookies/',                     views.cookies,                  name='cookies'),
]
