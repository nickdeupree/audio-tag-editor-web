"""
CORS and other configuration settings for the FastAPI app.
"""
import os

# YTMusic API settings
CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "../../client_secrets.json")
OAUTH_CREDENTIALS_FILE = os.path.join(os.path.dirname(__file__), "../../oauth.json")
REDIRECT_URI = "http://localhost:8000/api/ytmusic/oauth-callback"
SCOPES = ["https://www.googleapis.com/auth/youtube"]

# YouTube Music OAuth client ID and secret
YT_OAUTH_CLIENT_ID: str = "1045728791819-64eun01e0169rov4jei10v183pra9kbe.apps.googleusercontent.com"
YT_OAUTH_CLIENT_SECRET: str = "1045728791819-64eun01e0169rov4jei10v183pra9kbe.apps.googleusercontent.com"

# CORS settings
CORS_ORIGINS = [
    "http://localhost:3000",  # Next.js default port
    "http://127.0.0.1:3000",
]

CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# Server settings
HOST = "0.0.0.0"
PORT = 8000
