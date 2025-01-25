# users/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals  # Ensure this is the correct path to your signals file
        from .signals import create_default_users
        post_migrate.connect(create_default_users, sender=self)
