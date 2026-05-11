# commandes/models.py
from django.db import models

WILAYAS = [
    ('01','01 - Adrar'),('02','02 - Chlef'),('03','03 - Laghouat'),
    ('04','04 - Oum El Bouaghi'),('05','05 - Batna'),('06','06 - Béjaïa'),
    ('07','07 - Biskra'),('08','08 - Béchar'),('09','09 - Blida'),
    ('10','10 - Bouira'),('11','11 - Tamanrasset'),('12','12 - Tébessa'),
    ('13','13 - Tlemcen'),('14','14 - Tiaret'),('15','15 - Tizi Ouzou'),
    ('16','16 - Alger'),('17','17 - Djelfa'),('18','18 - Jijel'),
    ('19','19 - Sétif'),('20','20 - Saïda'),('21','21 - Skikda'),
    ('22','22 - Sidi Bel Abbès'),('23','23 - Annaba'),('24','24 - Guelma'),
    ('25','25 - Constantine'),('26','26 - Médéa'),('27','27 - Mostaganem'),
    ('28',"28 - M'Sila"),('29','29 - Mascara'),('30','30 - Ouargla'),
    ('31','31 - Oran'),('32','32 - El Bayadh'),('33','33 - Illizi'),
    ('34','34 - Bordj Bou Arréridj'),('35','35 - Boumerdès'),('36','36 - El Tarf'),
    ('37','37 - Tindouf'),('38','38 - Tissemsilt'),('39','39 - El Oued'),
    ('40','40 - Khenchela'),('41','41 - Souk Ahras'),('42','42 - Tipaza'),
    ('43','43 - Mila'),('44',"44 - Aïn Defla"),('45','45 - Naâma'),
    ('46',"46 - Aïn Témouchent"),('47','47 - Ghardaïa'),('48','48 - Relizane'),
    ('49','49 - Timimoun'),('50','50 - Bordj Badji Mokhtar'),
    ('51','51 - Ouled Djellal'),('52','52 - Béni Abbès'),
    ('53','53 - In Salah'),('54','54 - In Guezzam'),
    ('55','55 - Touggourt'),('56','56 - Djanet'),
    ('57',"57 - El M'Ghair"),('58','58 - El Meniaa'),
]

TYPE_LIVRAISON = [
    ('retrait',   'Retrait à la boutique'),
    ('livraison', 'Livraison à domicile'),
]

MODE_PAIEMENT = [
    ('cod', 'Paiement à la livraison (COD)'),
    ('ccp', 'Virement CCP / BaridiMob'),
]

STATUT_CHOICES = [
    ('en_attente',        'En attente de confirmation'),
    ('confirmee',         'Confirmée'),
    ('attente_paiement',  'En attente de paiement'),
    ('paiement_recu',     'Preuve de paiement reçue'),
    ('expediee',          'Expédiée'),
    ('livree',            'Livrée'),
    ('annulee',           'Annulée'),
]

STATUT_COULEUR = {
    'en_attente':       'bg-yellow-100 text-yellow-800',
    'confirmee':        'bg-blue-100 text-blue-800',
    'attente_paiement': 'bg-orange-100 text-orange-800',
    'paiement_recu':    'bg-purple-100 text-purple-800',
    'expediee':         'bg-indigo-100 text-indigo-800',
    'livree':           'bg-green-100 text-green-800',
    'annulee':          'bg-red-100 text-red-800',
}


class Order(models.Model):
    nom_client     = models.CharField(max_length=100)
    telephone      = models.CharField(max_length=20)
    email_client   = models.EmailField(blank=True, help_text='Pour recevoir la confirmation par email')
    type_livraison = models.CharField(max_length=10, choices=TYPE_LIVRAISON, default='livraison')
    wilaya         = models.CharField(max_length=2, choices=WILAYAS, blank=True)
    commune        = models.CharField(max_length=100, blank=True)
    adresse        = models.TextField(blank=True)
    mode_paiement  = models.CharField(max_length=10, choices=MODE_PAIEMENT, default='cod')
    preuve_paiement = models.ImageField(upload_to='preuves/', blank=True, null=True)
    statut         = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    total          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    notes          = models.TextField(blank=True)
    date_commande  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Commande'
        verbose_name_plural = 'Commandes'
        ordering = ['-date_commande']

    def __str__(self):
        return f'Commande #{self.pk} — {self.nom_client}'

    @property
    def statut_css(self):
        return STATUT_COULEUR.get(self.statut, 'bg-gray-100 text-gray-800')


class OrderItem(models.Model):
    commande      = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    produit       = models.ForeignKey('catalogue.Product', on_delete=models.PROTECT)
    quantite      = models.PositiveIntegerField(default=1)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.quantite}× {self.produit.titre}'

    @property
    def sous_total(self):
        return self.quantite * self.prix_unitaire
