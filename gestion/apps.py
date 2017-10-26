from __future__ import unicode_literals

from django.apps import AppConfig


class GestionConfig(AppConfig):
    name = 'gestion'

    def ready(self):
        import django.db.models.signals
