# commandes/views.py
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Sum, Count, Q
from django.utils import timezone
from catalogue.models import Product
from .models import Order, OrderItem
from .forms import CheckoutForm, SuiviCommandeForm, UploaderPreuveForm
from .emails import envoyer_confirmation_commande, envoyer_confirmation_admin


# ── Helpers session ─────────────────────────────────────
def get_cart(request):
    return request.session.get('cart', {})

def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ── Ajouter au panier ───────────────────────────────────
def add_to_cart(request, product_id):
    if request.method != 'POST':
        return redirect('catalogue:home')
    produit = get_object_or_404(Product, pk=product_id)
    if not produit.is_in_stock:
        messages.error(request, 'Ce produit est en rupture de stock.')
        return redirect('catalogue:product_detail', slug=produit.slug)
    quantite = max(1, int(request.POST.get('quantity', 1)))
    cart = get_cart(request)
    key  = str(product_id)
    if key in cart:
        cart[key]['quantite'] += quantite
    else:
        cart[key] = {
            'quantite': quantite,
            'prix': str(produit.prix_vente if produit.prix_vente else produit.prix_regulier),
            'nom':  produit.titre,
        }
    if cart[key]['quantite'] > produit.stock_quantite:
        cart[key]['quantite'] = produit.stock_quantite
    save_cart(request, cart)
    messages.success(request, f'« {produit.titre} » ajouté au panier.')
    return redirect('commandes:cart')


# ── Mettre à jour la quantité (AJAX) ────────────────────
def update_cart(request, product_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'method'}, status=405)

    cart = get_cart(request)
    key  = str(product_id)
    qty  = int(request.POST.get('quantity', 1))

    if key in cart:
        if qty <= 0:
            cart.pop(key)
            save_cart(request, cart)
            return JsonResponse({'removed': True, 'cart_count': len(cart), 'cart_total': str(_cart_total(cart))})
        else:
            try:
                produit = Product.objects.get(pk=product_id)
                cart[key]['quantite'] = min(qty, produit.stock_quantite)
            except Product.DoesNotExist:
                cart.pop(key)

    save_cart(request, cart)
    items, total = _build_cart_items(cart)
    item_data = next((i for i in items if str(i['produit'].pk) == key), None)
    return JsonResponse({
        'removed':     False,
        'quantite':    cart[key]['quantite'] if key in cart else 0,
        'sous_total':  str(item_data['sous_total']) if item_data else '0',
        'cart_total':  str(total),
        'cart_count':  len(cart),
    })


# ── Supprimer du panier ─────────────────────────────────
def remove_from_cart(request, product_id):
    cart = get_cart(request)
    cart.pop(str(product_id), None)
    save_cart(request, cart)
    return redirect('commandes:cart')


# ── Voir le panier ──────────────────────────────────────
def cart_view(request):
    cart  = get_cart(request)
    items, total = _build_cart_items(cart)
    return render(request, 'commandes/cart.html', {'items': items, 'total': total})


# ── Checkout ────────────────────────────────────────────
def checkout_view(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Votre panier est vide.')
        return redirect('catalogue:boutique')
    items, total = _build_cart_items(cart)

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.total = total
            # Livraison → virement obligatoire / Retrait → paiement sur place
            order.mode_paiement = 'ccp' if order.type_livraison == 'livraison' else 'cod'
            order.save()
            for item in items:
                OrderItem.objects.create(
                    commande=order, produit=item['produit'],
                    quantite=item['quantite'], prix_unitaire=item['prix'],
                )
                p = item['produit']
                p.stock_quantite = max(0, p.stock_quantite - item['quantite'])
                p.save(update_fields=['stock_quantite'])
            save_cart(request, {})
            envoyer_confirmation_commande(order)
            envoyer_confirmation_admin(order)
            return redirect('commandes:order_success', pk=order.pk)
    else:
        form = CheckoutForm()
    return render(request, 'commandes/checkout.html', {'form': form, 'items': items, 'total': total})


# ── Confirmation ────────────────────────────────────────
def order_success(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'commandes/order_success.html', {'order': order})


# ── Suivi commande (sans login) ─────────────────────────
def suivi_view(request):
    form   = SuiviCommandeForm(request.GET or None)
    orders = []
    recherche = ''

    if form.is_valid():
        recherche = form.cleaned_data['recherche'].strip()
        if recherche.isdigit() and len(recherche) <= 6:
            orders = Order.objects.filter(pk=recherche)
        else:
            orders = Order.objects.filter(telephone__icontains=recherche)

    return render(request, 'commandes/suivi.html', {
        'form': form,
        'orders': orders,
        'recherche': recherche,
    })


# ── Upload preuve de paiement ───────────────────────────
def upload_preuve(request):
    form  = UploaderPreuveForm(request.POST or None, request.FILES or None)
    succes = False

    if request.method == 'POST' and form.is_valid():
        numero = form.cleaned_data['numero_commande']
        tel    = form.cleaned_data['telephone'].strip().replace(' ', '').replace('-', '')
        try:
            order = Order.objects.get(pk=numero, telephone=tel)
            order.preuve_paiement = form.cleaned_data['preuve']
            order.statut = 'paiement_recu'
            order.save()
            succes = True
        except Order.DoesNotExist:
            form.add_error(None, 'Commande introuvable. Vérifiez le numéro et le téléphone.')

    return render(request, 'commandes/upload_preuve.html', {'form': form, 'succes': succes})


# ── Dashboard admin ────────────────────────────────────
@staff_member_required
def dashboard(request):
    aujourd_hui   = timezone.now().date()
    debut_semaine = aujourd_hui - timezone.timedelta(days=7)
    debut_mois    = aujourd_hui.replace(day=1)

    commandes_all = Order.objects.all()

    stats = {
        'today':          commandes_all.filter(date_commande__date=aujourd_hui).count(),
        'semaine':        commandes_all.filter(date_commande__date__gte=debut_semaine).count(),
        'mois':           commandes_all.filter(date_commande__date__gte=debut_mois).count(),
        'total':          commandes_all.count(),
        'ca_total':       commandes_all.exclude(statut='annulee').aggregate(s=Sum('total'))['s'] or 0,
        'ca_mois':        commandes_all.filter(date_commande__date__gte=debut_mois).exclude(statut='annulee').aggregate(s=Sum('total'))['s'] or 0,
        'en_attente':     commandes_all.filter(statut='en_attente').count(),
        'confirmees':     commandes_all.filter(statut='confirmee').count(),
        'att_paiement':   commandes_all.filter(statut='attente_paiement').count(),
        'paiement_recu':  commandes_all.filter(statut='paiement_recu').count(),
        'expediees':      commandes_all.filter(statut='expediee').count(),
        'livrees':        commandes_all.filter(statut='livree').count(),
        'annulees':       commandes_all.filter(statut='annulee').count(),
        'nb_produits':    Product.objects.count(),
        'ruptures':       Product.objects.filter(stock_quantite=0).count(),
    }

    dernieres_commandes = commandes_all[:10]

    return render(request, 'commandes/dashboard.html', {
        'stats': stats,
        'dernieres_commandes': dernieres_commandes,
    })


# ── Helper total panier ─────────────────────────────────
def _cart_total(cart):
    total = Decimal('0')
    for pid, data in cart.items():
        try:
            total += Decimal(data['prix']) * data['quantite']
        except Exception:
            pass
    return total


# ── Helper interne ──────────────────────────────────────
def _build_cart_items(cart):
    items = []
    total = Decimal('0')
    for pid, data in cart.items():
        try:
            produit    = Product.objects.get(pk=pid)
            prix       = Decimal(data['prix'])
            quantite   = data['quantite']
            sous_total = prix * quantite
            items.append({'produit': produit, 'quantite': quantite,
                          'prix': prix, 'sous_total': sous_total})
            total += sous_total
        except Product.DoesNotExist:
            pass
    return items, total
