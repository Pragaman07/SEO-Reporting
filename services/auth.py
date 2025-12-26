import os
import json
from google.oauth2 import service_account

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

def get_credentials():
    """
    Returns Google Cloud Credentials.
    1. Checks for 'GOOGLE_CREDENTIALS' env var (Production/Vercel).
    2. Fallback to 'credentials.json' (Local Dev).
    """
    # 1. Environment Variable (Vercel)
    env_creds = os.environ.get('GOOGLE_CREDENTIALS')
    if env_creds:
        try:
            creds_dict = json.loads(env_creds)
            return service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        except json.JSONDecodeError:
            raise ValueError("Error: GOOGLE_CREDENTIALS env var is not valid JSON.")

    # 2. Local File (Dev)
    local_file = 'credentials.json'
    if os.path.exists(local_file):
        return service_account.Credentials.from_service_account_file(local_file, scopes=SCOPES)
    
    # 3. Fail
    raise FileNotFoundError(
        "No credentials found. Set 'GOOGLE_CREDENTIALS' env var or place 'credentials.json' in root."
    )
