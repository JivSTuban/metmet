from django.apps import AppConfig

class VeterinariansConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'veterinarians'

    def ready(self):
        from . import signals  # Import signals here to avoid circular imports
