import requests

from typing import Dict
from customs.exceptions import UnauthorizedException
from customs.strategies.oauth2_strategy import OAuth2Strategy


class GoogleStrategy(OAuth2Strategy):
    """Authentication using Google as an OAuth2 provider.
    """

    name = "google"
    scopes = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
    ]

    authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url = "https://www.googleapis.com/oauth2/v4/token"
    refresh_url = "https://www.googleapis.com/oauth2/v4/token"
    user_profile_endpoint = "https://www.googleapis.com/oauth2/v1/userinfo"

    def validate_token(self) -> Dict:
        """Method to validate a Google token with Google.

        Raises:
            UnauthorizedException: When the user isn't authenticated or token is not valid

        Returns:
            Dict: The data from the token
        """

        try:
            # Get the token
            access_token = self.token["access_token"]
            validate_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"

            # No OAuth2Session is needed, just a plain GET request
            data = requests.get(validate_url).json()
            return data

        except Exception:
            raise UnauthorizedException()
