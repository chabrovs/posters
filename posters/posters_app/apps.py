from django.apps import AppConfig


class PostersAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posters_app'

    def ready(self):
        import posters_app.signals