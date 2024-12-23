from django.contrib.auth import get_user_model
from django.conf import settings
import msal

User = get_user_model()

class AzureADBackend:
    def authenticate(self, request, code=None):
        if not code:
            return None
            
        app = msal.ConfidentialClientApplication(
            settings.AZURE_AD_AUTH['CLIENT_ID'],
            authority=settings.AZURE_AD_AUTH['AUTHORITY'],
            client_credential=settings.AZURE_AD_AUTH['CLIENT_SECRET'],
        )

        try:
            result = app.acquire_token_by_authorization_code(
                code,
                scopes=settings.AZURE_AD_AUTH['SCOPE'],
                redirect_uri=settings.AZURE_AD_AUTH['REDIRECT_URI']
            )

            if 'error' in result:
                return None

            # Get user info from the access token
            user_info = result.get('id_token_claims')
            if not user_info:
                return None

            # Get or create user
            email = user_info.get('email', user_info.get('preferred_username'))
            if not email:
                return None

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'first_name': user_info.get('given_name', ''),
                    'last_name': user_info.get('family_name', ''),
                    'is_active': True
                }
            )
            return user
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 