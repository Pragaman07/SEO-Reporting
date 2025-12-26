import os
import json
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/webmasters.readonly',
    'https://www.googleapis.com/auth/analytics.readonly',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

def get_credentials():
    """
    Returns Google Cloud Credentials using OAuth 2.0 Token.
    1. Checks for 'GOOGLE_TOKEN' env var (Production/Vercel).
    2. Fallback to 'token.json' (Local Dev).
    Note: 'credentials.json' is NOT used for auth here, only for generating the token initially.
    """
    creds = None
    
    # 1. Environment Variable (Vercel Production)
    env_token = os.environ.get('GOOGLE_TOKEN')
    if env_token:
        try:
            token_info = json.loads(env_token)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except json.JSONDecodeError:
            print("Error: GOOGLE_TOKEN env var is not valid JSON.")

    # 2. Local File (Dev Fallback)
    if not creds and os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception as e:
            print(f"Error reading token.json: {e}")

    # 3. Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            print(f"Error refreshing token: {e}")
            # If refresh fails in serverless, we generally can't fix it without re-auth locally
            # But let's raise so the UI knows.
            raise e

    if not creds or not creds.valid:
        raise ValueError(
            "No valid token found. In Vercel, set 'GOOGLE_TOKEN' env var to the content of 'token.json'."
        )

    return creds
