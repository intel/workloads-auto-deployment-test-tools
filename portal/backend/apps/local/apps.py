from django.apps import AppConfig


class LocalConfig(AppConfig):
    name = 'local'

    def ready(self):
        import local.signals
