from datetime import date, datetime
import pandas as pd
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from cryptography.fernet import Fernet
from optimus_ids import Optimus
from django.conf import settings
import pyodbc

def get_db_password():
    # For development, return hardcoded password
    return 'KhCc@2024!'

def get_azure_db_connection():
    # Hardcoded connection settings for development
    connection_params = {
        'DRIVER': '{ODBC Driver 17 for SQL Server}',
        'SERVER': 'aidi-db-server.database.windows.net',
        'DATABASE': 'AIDI-DB',
        'UID': 'aidiadmin',
        'PWD': get_db_password(),
    }
    
    conn_str = (
        f"DRIVER={connection_params['DRIVER']};"
        f"SERVER={connection_params['SERVER']};"
        f"DATABASE={connection_params['DATABASE']};"
        f"UID={connection_params['UID']};"
        f"PWD={connection_params['PWD']};"
        "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
    )
    
    conn = pyodbc.connect(conn_str)
    return conn

def get_optimus_keys():
    # Hardcoded values for development - using the correct values
    return (73328341, 932428994)  # These are the correct values from your Streamlit app

def en_mrn(mrn):
    try:
        oprime, orandom = get_optimus_keys()
        print(f"Using Optimus keys: prime={oprime}, random={orandom}")  # Debug print
        my_optimus = Optimus(prime=oprime, random=orandom)
        encoded = my_optimus.encode(int(mrn))
        print(f"Successfully encoded {mrn} to {encoded}")  # Debug print
        return encoded
    except Exception as e:
        print(f"Error encoding MRN: {str(e)}")  # Debug print
        import traceback
        print(traceback.format_exc())  # Print full traceback
        raise

def de_mrn(mrn_en):
    oprime, orandom = get_optimus_keys()
    my_optimus = Optimus(prime=oprime, random=orandom)
    return my_optimus.decode(mrn_en)

def de_name(name):
    # For development, return the name as-is
    if settings.DEBUG:
        return name
    
    # Production Key Vault logic
    credential = ManagedIdentityCredential()
    client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
    fkey_secret = client.get_secret("fernetkey")
    fkey = fkey_secret.value
    fernet = Fernet(fkey)
    return fernet.decrypt(name).decode()

def retrieve_mrn_data(search_mrn, cursor):
    try:
        x = int(search_mrn)
        encoded_mrn = en_mrn(x)  # Encode the MRN
        print(f"Original MRN: {x}")  # Debug print
        print(f"Encoded MRN: {encoded_mrn}")  # Debug print
        
        # Use the exact same query as in your Streamlit app
        query = "SELECT * FROM vw_PatientWithBloodGroup WHERE MRN = ?"
        print(f"Query: {query} with MRN={encoded_mrn}")  # Debug print
        
        cursor.execute(query, (encoded_mrn,))
        rec = cursor.fetchone()
        
        if rec:
            print("Record found!")  # Debug print
        else:
            print("No record found")  # Debug print
            
        return rec
    except Exception as e:
        print(f"Error in retrieve_mrn_data: {str(e)}")  # Debug print
        import traceback
        print(traceback.format_exc())  # Print full traceback
        return None

def calculate_age(birth_date):
    try:
        today = date.today()
        
        # Convert datetime to date if needed
        if isinstance(birth_date, datetime):
            birth_date = birth_date.date()
            
        years = today.year - birth_date.year
        last_birthday = birth_date.replace(year=today.year)
        
        if last_birthday > today:
            last_birthday = birth_date.replace(year=today.year - 1)
            years -= 1
            
        days_in_year = (date(today.year + 1, 1, 1) - date(today.year, 1, 1)).days
        days_since_last_birthday = (today - last_birthday).days
        age = years + (days_since_last_birthday / days_in_year)
        
        # Round to one decimal place
        return round(age, 1)
    except Exception as e:
        print(f"Error calculating age: {str(e)}")  # Debug print
        return None 