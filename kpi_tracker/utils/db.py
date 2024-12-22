from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from django.conf import settings
import pyodbc

def get_db_password():
    credential = ManagedIdentityCredential()
    client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    retrieved_secret = client.get_secret(settings.AZURE_KEY_VAULT_SECRET_NAME)
    return retrieved_secret.value

def get_azure_db_connection():
    password = get_db_password()
    conn = pyodbc.connect(
        f'DRIVER={settings.DATABASES["default"]["OPTIONS"]["driver"]};'
        f'SERVER={settings.DATABASES["default"]["HOST"]};'
        f'PORT={settings.DATABASES["default"]["PORT"]};'
        f'DATABASE={settings.DATABASES["default"]["NAME"]};'
        f'UID={settings.DATABASES["default"]["USER"]};'
        f'PWD={password}'
    )
    return conn 