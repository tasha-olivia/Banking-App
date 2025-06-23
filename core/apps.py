from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError
        User = get_user_model()
        try:
            user, created = User.objects.get_or_create(
                username='manager',
                defaults={
                    'email': 'manager@gmail.com',
                }
            )
            user.is_manager = True
            user.is_staff = True
            user.set_password('AdminPassword')  # Always set password
            user.save()
        except OperationalError:
            pass