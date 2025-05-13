from django.apps import AppConfig


class FinAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fin_app'

    def ready(self):
        import fin_app.signals