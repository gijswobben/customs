from typing import Dict
from customs.exceptions import UnauthorizedException
from customs.strategies.oauth2_strategy import OAuth2Strategy

from requests_oauthlib import OAuth2Session  # type: ignore
from requests_oauthlib.compliance_fixes import facebook_compliance_fix  # type: ignore


class FacebookStrategy(OAuth2Strategy):
    """Authentication using Facebook as an OAuth2 provider."""

    name = "facebook"
    scopes = ["email", "public_profile"]
    fields = ["id", "name", "first_name", "last_name", "picture", "email"]

    authorization_base_url = "https://www.facebook.com/dialog/oauth"
    token_url = "https://graph.facebook.com/oauth/access_token"
    refresh_url = "https://graph.facebook.com/oauth/access_token"
    user_profile_endpoint = "https://graph.facebook.com/me?"

    def get_user_info(self) -> Dict:
        """Method to get user info for the logged in user.

        Raises:
            UnauthorizedException: When the user is not authenticated

        Returns:
            Dict: The user profile
        """

        try:

            # Get the token
            token = self.token

            # Helper method to update the token in the session
            def token_updater(token):
                self.token = token

            # Get a session with auto-refresh of the token
            client = OAuth2Session(
                self.client_id,
                token=token,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                auto_refresh_url=self.refresh_url,
                token_updater=token_updater,
            )

            if self.name == "facebook":
                facebook_compliance_fix(client)

            # Return the user info
            return client.get(
                self.user_profile_endpoint + "fields=" + ",".join(self.fields)
            ).json()

        except Exception:
            raise UnauthorizedException()
