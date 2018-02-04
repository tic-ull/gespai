# coding:utf-8
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from gestion.models import CambiosPendientes
from django.contrib.auth.models import Group
from notifications.signals import notify
from notifications.models import Notification


@receiver(post_save, sender=CambiosPendientes)
def cambio_estado(sender, **kwargs):
    osl = Group.objects.get(name='osl')
    instance = kwargs.get('instance')
    # En caso de que ya haya una notificación para el cambio que se va a guardar
    # (si se modifica un cambio ya existente) se borra la notificación y se genera una nueva
    try:
        notificacion = Notification.objects.get(
            action_object_object_id=instance.pk)
        notificacion.delete()
    except Notification.DoesNotExist:
        pass
    if instance.plaza:
        desc = """
            Tipo de cambio: {}
            Plaza asociada al cambio: {}
            Fecha del cambio: {}
        """.format(
            instance.get_estado_cambio_display(),
            instance.plaza,
            instance.fecha_cambio.strftime('%d/%m/%Y'))
    else:
        desc = """
            Tipo de cambio: {}
            Fecha del cambio: {}
        """.format(
            instance.get_estado_cambio_display(),
            instance.fecha_cambio.strftime('%d/%m/%Y'))
    notify.send(
        instance.becario,
        recipient=osl,
        verb='tiene un nuevo cambio solicitado',
        action_object=instance,
        target=instance.becario,
        description=desc)


# Si se borra un cambio, se borra la notificación asociada al mismo
@receiver(post_delete, sender=CambiosPendientes)
def borrar_notificacion(sender, **kwargs):
    instance = kwargs.get('instance')
    try:
        notificacion = Notification.objects.get(
            action_object_object_id=instance.pk)
        notificacion.delete()
    except Notification.DoesNotExist:
        pass
