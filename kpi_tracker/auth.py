from django.conf import settings
import msal
import requests
from urllib.parse import urlencode

def get_auth_app():
    return msal.ConfidentialClientApplication(
        settings.AZURE_AD['CLIENT_ID'],
        authority=settings.AZURE_AD['AUTHORITY'],
        client_credential=settings.AZURE_AD['CLIENT_SECRET'],
    )

def get_auth_url():
    # Instead of using MSAL's authorization URL method directly,
    # let's build the URL ourselves
    base_url = f"{settings.AZURE_AD['AUTHORITY']}/oauth2/v2.0/authorize"
    
    params = {
        'client_id': settings.AZURE_AD['CLIENT_ID'],
        'response_type': 'code',
        'redirect_uri': settings.AZURE_AD['REDIRECT_URI'],
        'scope': ' '.join([
            'openid',
            'profile',
            'email',
            'User.Read'
        ]),
        'response_mode': 'query'
    }
    
    auth_url = f"{base_url}?{urlencode(params)}"
    print("Debug - Auth URL:", auth_url)
    return auth_url

def get_token_from_code(code):
    token_url = f"{settings.AZURE_AD['AUTHORITY']}/oauth2/v2.0/token"
    
    data = {
        'client_id': settings.AZURE_AD['CLIENT_ID'],
        'scope': ' '.join([
            'openid',
            'profile',
            'email',
            'User.Read'
        ]),
        'code': code,
        'redirect_uri': settings.AZURE_AD['REDIRECT_URI'],
        'grant_type': 'authorization_code',
        'client_secret': settings.AZURE_AD['CLIENT_SECRET']
    }
    
    response = requests.post(token_url, data=data)
    return response.json()

def get_user_info(token):
    if not token:
        print("No token provided to get_user_info")  # Debug print
        return None
        
    graph_url = 'https://graph.microsoft.com/v1.0/me'
    headers = {
        'Authorization': f'Bearer {token.get("access_token")}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(graph_url, headers=headers)
        print(f"Graph API response status: {response.status_code}")  # Debug print
        print(f"Graph API response: {response.text}")  # Debug print
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting user info: {response.text}")  # Debug print
            return None
    except Exception as e:
        print(f"Exception in get_user_info: {str(e)}")  # Debug print
        return None 