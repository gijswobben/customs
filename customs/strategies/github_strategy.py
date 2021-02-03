import requests

from typing import Dict
from customs.exceptions import UnauthorizedException
from customs.strategies.oauth2_strategy import OAuth2Strategy


class GithubStrategy(OAuth2Strategy):
    """Authentication using Github as an OAuth2 provider.
    """

    name = "github"
    scopes = ["user"]

    authorization_base_url = "https://github.com/login/oauth/authorize"
    token_url = "https://github.com/login/oauth/access_token"
    refresh_url = "https://github.com/login/oauth/access_token"
    user_profile_endpoint = "https://api.github.com/user"

    def validate_token(self) -> Dict:
        """Method to validate a Github token with Github.

        Raises:
            UnauthorizedException: When the user isn't authenticated or token is not valid

        Returns:
            Dict: The data from the token
        """

        try:
            # Get the token
            access_token = self.token["access_token"]
            validate_url = f"https://api.github.com/applications/{self.client_id}/tokens/{access_token}"

            # No OAuth2Session is needed, just a plain GET request
            data = requests.get(validate_url).json()
            return data

        except Exception as e:
            print(e)
            raise UnauthorizedException()
