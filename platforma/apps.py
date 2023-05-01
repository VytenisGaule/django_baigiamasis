from django.apps import AppConfig


class PlatformaConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'platforma'

    def ready(self):
        import platforma.signals
