import os

AZURE_AD = {
    'TENANT_ID': os.getenv('AZURE_AD_TENANT_ID'),
    'CLIENT_ID': os.getenv('AZURE_AD_CLIENT_ID'),
    'CLIENT_SECRET': os.getenv('AZURE_AD_CLIENT_SECRET'),
    'AUTHORITY': f'https://login.microsoftonline.com/{os.getenv("AZURE_AD_TENANT_ID")}',
    'REDIRECT_URI': os.getenv('AZURE_AD_REDIRECT_URI', 'http://khcc-datahub.azurewebsites.net/:8000/oauth2/callback/'),
    'SCOPE': ['User.Read', 'profile', 'email', 'openid'],
    'LOGOUT_URI': os.getenv('AZURE_AD_LOGOUT_URI', 'http://localhost:8000')
} 