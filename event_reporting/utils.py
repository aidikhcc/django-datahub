from django.db import connection
from datetime import datetime
from kpi_tracker.utils import en_mrn, de_mrn, get_optimus_keys
from django.conf import settings
from azure.identity import ManagedIdentityCredential
from azure.keyvault.secrets import SecretClient
from cryptography.fernet import Fernet

def retrieve_patient_info(mrn):
    """
    Retrieve patient information from VISTA_PATIENTS table using encoded MRN
    """
    try:
        # Get Optimus keys and encode MRN
        oprime, orandom = get_optimus_keys()
        print(f"Using Optimus keys: prime={oprime}, random={orandom}")
        
        x = int(mrn)
        encoded_mrn = en_mrn(x)
        print(f"Successfully encoded {mrn} to {encoded_mrn}")
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT TOP 1
                    DOB,
                    SEX,
                    NATIONALITY,
                    NAME
                FROM [dbo].[VISTA_PATIENTS]
                WHERE MRN = %s
            """, [encoded_mrn])
            
            row = cursor.fetchone()
            print(f"Raw database row: {row}")
            
            if row:
                dob, sex, nationality, encrypted_name = row
                print(f"Raw encrypted name: {encrypted_name}")
                
                # Calculate age
                if dob:
                    today = datetime.now()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                else:
                    age = None
                
                # Convert gender from MALE/FEMALE to Male/Female
                gender = sex.capitalize() if sex else None
                
                # Convert nationality if needed
                nationality = "Jordanian" if nationality == "JOR" else "Non Jordanian"
                
                # For development, use a direct Fernet key
                if settings.DEBUG:
                    fkey = b'H3khQspg__GrT8Llu_Pc9mDcY1ebADObnlYuGVv_hn4='  # Replace with your development Fernet key
                else:
                    # In production, get key from Azure Key Vault
                    credential = ManagedIdentityCredential()
                    client = SecretClient(vault_url=settings.AZURE_KEY_VAULT_URL, credential=credential)
                    fkey_secret = client.get_secret("fernetkey")
                    fkey = fkey_secret.value
                
                # Decrypt name
                patient_name = None
                if encrypted_name:
                    try:
                        # Remove the b' prefix and ' suffix if present
                        if isinstance(encrypted_name, str) and encrypted_name.startswith("b'") and encrypted_name.endswith("'"):
                            encrypted_name = encrypted_name[2:-1].encode()
                        elif isinstance(encrypted_name, str):
                            encrypted_name = encrypted_name.encode()
                        
                        # Create Fernet instance and decrypt
                        fernet = Fernet(fkey)
                        patient_name = fernet.decrypt(encrypted_name).decode()
                        print(f"Successfully decrypted name: {patient_name}")
                    except Exception as e:
                        print(f"Error decrypting name: {str(e)}")
                        print(f"Error type: {type(e)}")
                        print(f"Name type: {type(encrypted_name)}")
                    
                return {
                    'dob': dob,
                    'gender': gender,
                    'nationality': nationality,
                    'name': patient_name,
                    'age': age
                }
            return None
            
    except Exception as e:
        print(f"Error retrieving patient info: {str(e)}")
        return None 