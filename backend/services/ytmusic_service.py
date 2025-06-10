from ytmusicapi import YTMusic, OAuthCredentials
from config import settings
import subprocess
import os

def get_login_url():
    try:
        result = subprocess.run(['ytmusicapi', 'oauth'],
                                capture_output=True, 
                                text=True, 
                                cwd=os.path.dirname(settings.OAUTH_CREDENTIALS_FILE)
                    )
        url, code = None, None
        for line in result.stdout.split('\n'):
            if 'https://www.google.com/device' in line:
                url = line.strip()
            if 'Enter the code' in line and ':' in line:
                code = line.split(':')[-1].strip()
        if url and code:
            return {"auth_url": url, "user_code": code}
        return {"error": "Could not parse URL and code"}
    except Exception as e:
        return {"error": str(e)}

def complete_oauth(code: str):
    # The new OAuth flow doesn't use a callback with code
    # Instead, it creates oauth.json automatically
    pass

def get_ytmusic_client():
    oauth_file = settings.OAUTH_CREDENTIALS_FILE

    if not os.path.exists(oauth_file):
        return None
    
    oauth_credentials = OAuthCredentials(
        client_id=settings.CLIENT_ID,
        client_secret=settings.CLIENT_SECRET
    )
    
    return YTMusic(oauth_file, oauth_credentials=oauth_credentials)

# def get_playlists():
#     ytmusic = get_ytmusic_client()
#     if not ytmusic:
#         raise Exception("OAuth not completed")
#     return ytmusic.get_library_playlists()