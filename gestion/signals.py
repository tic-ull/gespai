from django.db.models.signals import post_save
from django.dispatch import receiver
from gestion.models import CambiosPendientes
from django.contrib.auth.models import Group
from notifications.signals import notify


@receiver(post_save, sender=CambiosPendientes)
def cambio_estado(sender, **kwargs):
    osl = Group.objects.get(name='osl')
    instance = kwargs.get('instance')
    notify.send(instance, recipient=osl, verb='ha pasado a estar asignado', action_object=instance)
