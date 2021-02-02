import os
import requests

from abc import ABC
from flask import (
    Flask,
    Blueprint,
    Request as FlaskRequest,
    session,
    redirect,
    url_for,
    request,
)
from werkzeug.wrappers import Request
from requests_oauthlib import OAuth2Session  # type: ignore

from customs.exceptions import UnauthorizedException
from customs.strategies.basestrategy import BaseStrategy

from typing import Any, Dict, List, Union


class GoogleStrategy(BaseStrategy, ABC):

    name: str = "google"
    authorization_base_url: str = "https://accounts.google.com/o/oauth2/v2/auth"
    token_url: str = "https://www.googleapis.com/oauth2/v4/token"
    refresh_url: str = "https://www.googleapis.com/oauth2/v4/token"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: List[str] = [
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
        enable_insecure: bool = False,
        endpoint_prefix: str = "/auth/google",
    ) -> None:

        # Store the input arguments
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.endpoint_prefix = endpoint_prefix

        # This should be disabled in production, but for testing we can stop enforcing HTTPS
        if enable_insecure:
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Initialize the rest of the strategy
        super().__init__(
            serialize_user_function=None,
            deserialize_user_function=None,
        )

        # Ensure sessions are enabled
        if self._customs is not None:
            assert (
                self._customs.use_sessions
            ), "Google authentication requires sessions to be enabled"

    @property
    def token(self) -> Dict:
        return session.get("oauth_token")

    @token.setter
    def token(self, new_value: Dict) -> None:
        session["oauth_token"] = new_value

    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:
        return self.token

    def get_google_user_info(self) -> Dict:
        """ Method to get user info for the logged in user, from Google.

        Raises:
            UnauthorizedException: When the user is not authenticated

        Returns:
            Dict: The user profile from Google
        """

        try:

            # Get the token
            token = self.token

            # Helper method to update the token in the session
            def token_updater(token):
                self.token = token

            # Get a session with auto-refresh of the token
            google = OAuth2Session(
                self.client_id,
                token=token,
                auto_refresh_kwargs={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                auto_refresh_url=self.refresh_url,
                token_updater=token_updater,
            )

            # Return the user info
            return google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()

        except Exception:
            raise UnauthorizedException()

    def validate_token(self) -> Dict:
        """ Method to validate a Google token with Google.

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

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        """ Method to authenticate a user

        Args:
            request (Union[Request, FlaskRequest]): [description]

        Raises:
            UnauthorizedException: [description]

        Returns:
            Any: [description]
        """

        # Deserialize the user from the session
        try:
            self.validate_token()
            return self.deserialize_user(session["user"])
        except Exception:
            raise UnauthorizedException()

    def register_additional_routes(self, app: Flask) -> None:
        """ Register additional routes, specific for this strategy.

        Args:
            app (Flask): The app to register the strategies to
        """

        # Create a blueprint to register all Google related endpoints
        google_blueprint = Blueprint(
            "google", __name__, url_prefix=self.endpoint_prefix
        )

        @google_blueprint.route("/login")
        def google_login():
            google = OAuth2Session(
                self.client_id,
                scope=self.scopes,
                redirect_uri=url_for(".google_callback", _external=True),
            )
            authorization_url, state = google.authorization_url(
                self.authorization_base_url,
                access_type="offline",
                prompt="select_account",
            )

            # State is used to prevent CSRF, keep this for later.
            session["oauth_state"] = state
            return redirect(authorization_url)

        @google_blueprint.route("/callback", methods=["GET"])
        def google_callback():
            google = OAuth2Session(
                self.client_id,
                state=session["oauth_state"],
                redirect_uri=url_for(".google_callback", _external=True),
            )
            self.token = google.fetch_token(
                self.token_url,
                client_secret=self.client_secret,
                authorization_response=request.url,
            )

            # Get additional data for the user
            google_user_data = self.get_google_user_info()

            # Ensure the user is registered
            user = self.get_or_create_user(google_user_data)

            # Store the (serialized) user info on the sessions
            session["user"] = self.serialize_user(user)

            # Redirect the user to the requested page
            if session.get("next") is not None:
                url = session["next"]
                del session["next"]
                return redirect(url)

            # Default is to redirect to the root
            return redirect("/")

        # Register the blueprint with the app
        app.register_blueprint(google_blueprint)
