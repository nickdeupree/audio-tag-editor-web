from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from services import ytmusic_service
from ytmusicapi import YTMusic, OAuthCredentials
from config.settings import YT_OAUTH_CLIENT_ID, YT_OAUTH_CLIENT_SECRET
import os

router = APIRouter(prefix="/api/ytmusic", tags=["ytmusic"])


@router.get("/login-url")
def login_url():
    return ytmusic_service.get_login_url()


@router.get("/oauth-callback")
def oauth_callback(request: Request):
    code = request.query_params.get("code")
    if not code:
        return JSONResponse({"error": "Missing code"}, status_code=400)

    ytmusic_service.complete_oauth(code)
    return RedirectResponse(url="/success")


@router.post("/login")
async def login_to_ytmusic():
    # This will create oauth.json in the current directory
    # and print a code to the console, which the user needs to enter at google.com/device
    # It's a blocking call, so the user will have to wait until the process is complete.
    # In a real-world scenario, you'd handle this asynchronously.
    try:
        YTMusic.setup(filepath="oauth.json", oauth_filepath="oauth.json")
        return {"message": "Login process initiated. Check console for instructions."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user-info")
async def get_user_info():
    try:
        if not os.path.exists("oauth.json"):
            raise HTTPException(status_code=401, detail="Not logged in. Please login first via /ytmusic/login")

        oauth_creds = OAuthCredentials(client_id=YT_OAUTH_CLIENT_ID, client_secret=YT_OAUTH_CLIENT_SECRET, filepath="oauth.json")
        ytmusic = YTMusic(auth="oauth.json", oauth_credentials=oauth_creds)

        # Attempt to get some user-specific data to verify login
        # For example, get playlists (though this might be empty for new users)
        # Or try to get library songs, which is a good indicator of a successful login.
        # The specific method to get user profile picture/info might vary or not be directly available.
        # We'll use get_library_playlists as a proxy for successful login and fetching some data.
        playlists = ytmusic.get_library_playlists(limit=1) # Limit to 1 to minimize data transfer

        # Placeholder for actual user info/profile picture retrieval if API supports it
        # ytmusicapi does not directly provide a method to get user's profile picture.
        # We can return a success message and potentially some basic info if available.
        # For now, confirming login by fetching playlists is the main goal.

        # If you have a way to get user's name or email through another Google API using the same OAuth token,
        # you could integrate that here. ytmusicapi is focused on music functionalities.

        return {"message": "Successfully logged in and fetched some data.", "data_example": playlists}
    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="OAuth file not found. Please login first.")
    except Exception as e:
        # Catching a broad exception here to handle various issues that might occur during API interaction
        raise HTTPException(status_code=500, detail=f"Failed to get user info: {str(e)}")

# @router.get("/playlists")
# def playlists():
#     return ytmusic_service.get_playlists()
