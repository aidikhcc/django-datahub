import os

AZURE_AD = {
    'TENANT_ID': os.getenv('AZURE_AD_TENANT_ID'),
    'CLIENT_ID': os.getenv('AZURE_AD_CLIENT_ID'),
    'CLIENT_SECRET': os.getenv('AZURE_AD_CLIENT_SECRET'),
    'AUTHORITY': f'https://login.microsoftonline.com/{os.getenv("AZURE_AD_TENANT_ID")}',
    'REDIRECT_URI': 'https://khcc-datahub.azurewebsites.net/oauth2/callback',
    'SCOPE': ['User.Read', 'profile', 'email', 'openid'],
    'LOGOUT_URI': 'https://khcc-datahub.azurewebsites.net/',
    'RESPONSE_TYPE': 'code',
    'RESPONSE_MODE': 'query'
} 