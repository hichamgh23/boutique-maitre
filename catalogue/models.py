from django.db import models


class Category(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'


class Product(models.Model):
    categorie = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    prix_regulier = models.DecimalField(max_digits=10, decimal_places=2)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stock_quantite = models.IntegerField(default=0)
    image_principale = models.ImageField(upload_to='produits/')

    @property
    def is_in_stock(self):
        return self.stock_quantite > 0

    def __str__(self):
        return self.titre

    class Meta:
        verbose_name = 'Produit'
        verbose_name_plural = 'Produits'
