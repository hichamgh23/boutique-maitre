# commandes/emails.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings


def envoyer_confirmation_commande(order):
    """Email envoyé au client dès que sa commande est enregistrée."""
    if not order.email_client:
        return

    sujet = f'Votre commande #{order.pk} a bien été reçue — {settings.BOUTIQUE_NOM}'
    contenu_html = render_to_string('commandes/emails/confirmation.html', {'order': order})
    contenu_txt  = render_to_string('commandes/emails/confirmation.txt',  {'order': order})

    send_mail(
        subject      = sujet,
        message      = contenu_txt,
        from_email   = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [order.email_client],
        html_message = contenu_html,
        fail_silently = True,
    )


def envoyer_confirmation_admin(order):
    """Email envoyé à l'admin pour chaque nouvelle commande."""
    admin_email = getattr(settings, 'ADMIN_ORDER_EMAIL', None)
    if not admin_email:
        return

    sujet = f'[Nouvelle commande] #{order.pk} — {order.nom_client} — {order.total} DA'
    contenu_txt = (
        f'Nouvelle commande reçue.\n\n'
        f'Client : {order.nom_client}\n'
        f'Téléphone : {order.telephone}\n'
        f'Email : {order.email_client or "Non renseigné"}\n'
        f'Mode : {order.get_type_livraison_display()}\n'
        f'Paiement : {order.get_mode_paiement_display()}\n'
        f'Total : {order.total} DA\n\n'
        f'Voir dans l\'admin : /admin/commandes/order/{order.pk}/change/'
    )
    send_mail(
        subject        = sujet,
        message        = contenu_txt,
        from_email     = settings.DEFAULT_FROM_EMAIL,
        recipient_list = [admin_email],
        fail_silently  = True,
    )
