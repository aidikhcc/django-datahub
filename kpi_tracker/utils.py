from datetime import date
import pandas as pd
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from cryptography.fernet import Fernet
from optimus_ids import Optimus
from django.conf import settings

def get_optimus_keys():
    credential = ManagedIdentityCredential()
    client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    
    # Get Optimus prime
    prime_secret = client.get_secret("optimus-prime")
    oprime = prime_secret.value
    
    # Get Optimus random
    random_secret = client.get_secret("optimus-random")
    orandom = random_secret.value
    
    return int(oprime), int(orandom)

def en_mrn(mrn):
    oprime, orandom = get_optimus_keys()
    my_optimus = Optimus(prime=oprime, random=orandom)
    return my_optimus.encode(mrn)

def de_mrn(mrn_en):
    oprime, orandom = get_optimus_keys()
    my_optimus = Optimus(prime=oprime, random=orandom)
    return my_optimus.decode(mrn_en)

def de_name(name):
    
    credential = ManagedIdentityCredential()
    client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    fkey_secret = client.get_secret("fernetkey")
    fkey = fkey_secret.value
    fernet = Fernet(fkey)
    return fernet.decrypt(name).decode()

def retrieve_mrn_data(search_mrn, cursor):
    x = int(search_mrn)
    cursor.execute("SELECT * FROM vw_PatientWithBloodGroup WHERE MRN = ?", (en_mrn(x),))
    rec = cursor.fetchone()
    return rec

def calculate_age(birth_date):
    today = date.today()
    years = today.year - birth_date.year
    last_birthday = birth_date.replace(year=today.year)
    if last_birthday > today:
        last_birthday = birth_date.replace(year=today.year - 1)
    days_in_year = (date(today.year + 1, 1, 1) - date(today.year, 1, 1)).days
    days_since_last_birthday = (today - last_birthday).days
    age = years + (days_since_last_birthday / days_in_year)
    return age