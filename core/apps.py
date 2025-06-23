from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        from django.contrib.auth import get_user_model
        from django.db.utils import OperationalError
        User = get_user_model()
        try:
            if not User.objects.filter(username='manager').exists():
                user = User.objects.create_user(
                    username='manager',
                    email='manager@gmail.com',
                    password='AdminPassword'
                )
                user.is_manager = True
                user.is_staff = True  # Optional: allows access to Django admin
                user.save()
        except OperationalError:
            # Database might not be ready yet (e.g., during migrate)
            pass