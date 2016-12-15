from django.db.models.signals import post_save
from django.dispatch import receiver
from gestion.models import CambiosPendientes
from django.contrib.auth.models import Group
from notifications.signals import notify


@receiver(post_save, sender=CambiosPendientes)
def cambio_estado(sender, **kwargs):
    osl = Group.objects.get(name='osl')
    instance = kwargs.get('instance')
    if instance.plaza:
        desc = 'Tipo de cambio: ' + instance.get_estado_cambio_display() + '\nPlaza asociada al cambio: ' + \
            unicode(instance.plaza) or 'Renuncia' + '\nFecha del cambio: ' + \
            instance.fecha_cambio.strftime('%d/%m/%Y')
    else:
        desc = 'Tipo de cambio: ' + instance.get_estado_cambio_display() + '\nFecha del cambio: ' + \
            instance.fecha_cambio.strftime('%d/%m/%Y')
    notify.send(instance.becario, recipient=osl, verb='tiene un nuevo cambio solicitado',
                action_object=instance, target=instance.becario, description=desc)
