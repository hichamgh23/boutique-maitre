from django.db import models


class BoutiqueSettings(models.Model):
    nom_boutique       = models.CharField(max_length=100, default='Ma Boutique')
    description        = models.TextField(blank=True, help_text='Message de bienvenue affiché sur la page d\'accueil')
    couleur_principale = models.CharField(max_length=7, default='#0d6efd')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Configuration Boutique'
        verbose_name_plural = 'Configuration Boutique'
