# commandes/forms.py
from django import forms
from .models import Order

INPUT = ('w-full border border-gray-200 rounded-xl px-4 py-3.5 text-base text-gray-900 '
         'focus:outline-none focus:ring-2 transition-all')


class CheckoutForm(forms.ModelForm):
    class Meta:
        model  = Order
        fields = ['nom_client', 'telephone', 'email_client', 'type_livraison',
                  'wilaya', 'commune', 'adresse', 'notes']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['nom_client'].widget.attrs.update({
            'class': INPUT,
            'placeholder': 'Votre nom complet',
            'autocomplete': 'name',
            'inputmode': 'text',
        })
        self.fields['telephone'].widget.attrs.update({
            'class': INPUT,
            'placeholder': '0555 12 34 56',
            'autocomplete': 'tel-national',
            'inputmode': 'tel',
            'type': 'tel',
        })
        self.fields['email_client'].widget.attrs.update({
            'class': INPUT,
            'placeholder': 'votre@email.com (optionnel)',
            'autocomplete': 'email',
            'inputmode': 'email',
        })
        self.fields['wilaya'].widget.attrs.update({'class': INPUT})
        self.fields['commune'].widget.attrs.update({
            'class': INPUT,
            'placeholder': 'Votre commune',
            'autocomplete': 'address-level2',
        })
        self.fields['adresse'].widget = forms.Textarea(attrs={
            'class': INPUT,
            'rows': 3,
            'placeholder': 'Rue, numéro, quartier...',
            'autocomplete': 'street-address',
        })
        self.fields['notes'].widget = forms.Textarea(attrs={
            'class': INPUT + ' resize-none',
            'rows': 2,
            'placeholder': 'Instructions spéciales (optionnel)',
        })

        self.fields['wilaya'].required    = False
        self.fields['commune'].required   = False
        self.fields['adresse'].required   = False
        self.fields['email_client'].required = False

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('type_livraison') == 'livraison':
            if not cleaned.get('wilaya'):
                self.add_error('wilaya', 'La wilaya est obligatoire pour une livraison.')
            if not cleaned.get('commune'):
                self.add_error('commune', 'La commune est obligatoire.')
        return cleaned

    def clean_telephone(self):
        import re
        tel = self.cleaned_data.get('telephone', '').strip()
        # Garde uniquement les chiffres
        tel = re.sub(r'\D', '', tel)
        # +213XXXXXXXXX ou 213XXXXXXXXX → 0XXXXXXXXX
        if tel.startswith('213') and len(tel) == 12:
            tel = '0' + tel[3:]
        if len(tel) < 8:
            raise forms.ValidationError('Numéro trop court.')
        return tel


class SuiviCommandeForm(forms.Form):
    recherche = forms.CharField(
        label='Numéro de commande ou téléphone',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': INPUT,
            'placeholder': 'Ex : 12345  ou  0555123456',
            'inputmode': 'text',
            'autocomplete': 'off',
        })
    )


class UploaderPreuveForm(forms.Form):
    numero_commande = forms.IntegerField(
        label='Numéro de commande',
        widget=forms.NumberInput(attrs={
            'class': INPUT,
            'placeholder': 'Ex : 12345',
            'inputmode': 'numeric',
        })
    )
    telephone = forms.CharField(
        label='Téléphone (utilisé lors de la commande)',
        max_length=20,
        widget=forms.TextInput(attrs={
            'class': INPUT,
            'placeholder': '0555 12 34 56',
            'inputmode': 'tel',
            'type': 'tel',
        })
    )
    preuve = forms.ImageField(
        label="Capture d'écran / Photo du virement",
        widget=forms.FileInput(attrs={
            'class': INPUT,
            'accept': 'image/*',
            'capture': 'environment',
        })
    )
