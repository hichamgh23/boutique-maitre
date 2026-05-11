from .models import BoutiqueSettings


def boutique_config_processor(request):
    return {'config': BoutiqueSettings.objects.first()}
