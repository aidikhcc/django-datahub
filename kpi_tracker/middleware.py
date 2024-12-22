from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class DevelopmentAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            # Get or create a superuser
            superuser, created = User.objects.get_or_create(
                username='admin',
                defaults={
                    'email': 'admin@example.com',
                    'is_staff': True,
                    'is_superuser': True,
                    'is_active': True,
                    'first_name': 'Admin',
                    'last_name': 'User'
                }
            )
            request.user = superuser

        response = self.get_response(request)
        return response 