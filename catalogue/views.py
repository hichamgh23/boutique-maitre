# catalogue/views.py
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.db.models import Q
from .models import Product, Category


def home_view(request):
    meilleures_ventes = Product.objects.all()[:8]
    return render(request, 'catalogue/home.html', {
        'meilleures_ventes': meilleures_ventes,
    })


def boutique_view(request):
    categories     = Category.objects.all()
    cat_slug       = request.GET.get('categorie')
    query          = request.GET.get('q', '').strip()
    categorie_active = None

    produits = Product.objects.select_related('categorie').all()

    if cat_slug:
        produits = produits.filter(categorie__slug=cat_slug)
        categorie_active = get_object_or_404(Category, slug=cat_slug)

    if query:
        produits = produits.filter(
            Q(titre__icontains=query) | Q(description__icontains=query)
        )

    paginator = Paginator(produits, 12)
    page      = request.GET.get('page', 1)
    produits_page = paginator.get_page(page)

    return render(request, 'catalogue/boutique.html', {
        'produits':          produits_page,
        'categories':        categories,
        'categorie_active':  categorie_active,
        'query':             query,
        'total_count':       paginator.count,
    })


def product_detail(request, slug):
    produit = get_object_or_404(Product, slug=slug)
    return render(request, 'catalogue/product_detail.html', {'produit': produit})


def contact_view(request):
    return render(request, 'catalogue/contact.html')


def comment_ca_marche(request):
    return render(request, 'catalogue/comment_ca_marche.html')


def politique_confidentialite(request):
    return render(request, 'catalogue/politique_confidentialite.html')


def cookies(request):
    return render(request, 'catalogue/cookies.html')


def search_api(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse({'results': [], 'count': 0})

    produits = Product.objects.filter(
        Q(titre__icontains=q) | Q(description__icontains=q)
    ).select_related('categorie')[:8]

    results = []
    for p in produits:
        results.append({
            'titre':     p.titre,
            'slug':      p.slug,
            'prix':      str(p.prix_vente if p.prix_vente else p.prix_regulier),
            'prix_barre': str(p.prix_regulier) if p.prix_vente else None,
            'image':     p.image_principale.url if p.image_principale else None,
            'categorie': p.categorie.nom if p.categorie else '',
            'in_stock':  p.is_in_stock,
            'url':       f'/produit/{p.slug}/',
        })

    return JsonResponse({'results': results, 'count': len(results)})
