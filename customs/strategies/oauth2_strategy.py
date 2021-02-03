import os
import warnings

from abc import abstractmethod
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
from requests_oauthlib.compliance_fixes import facebook_compliance_fix  # type: ignore

from customs.exceptions import UnauthorizedException
from customs.strategies.base_strategy import BaseStrategy

from typing import Any, Dict, List, Optional, Union


class OAuth2Strategy(BaseStrategy):
    """[summary]

    Args:
        client_id (str): [description]
        client_secret (str): [description]
        scopes (Optional[List[str]], optional): [description]. Defaults to None.
        enable_insecure (bool, optional): [description]. Defaults to False.
        endpoint_prefix (Optional[str], optional): [description]. Defaults to None.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scopes: Optional[List[str]] = None,
        enable_insecure: bool = False,
        endpoint_prefix: Optional[str] = None,
    ) -> None:

        # Store the input arguments
        self.client_id = client_id
        self.client_secret = client_secret

        if scopes is not None:
            self.scopes = scopes  # type: ignore

        if endpoint_prefix is None:
            self.endpoint_prefix = f"/auth/{self.name}"
        else:
            self.endpoint_prefix = endpoint_prefix

        # This should be disabled in production, but for testing we can stop enforcing HTTPS
        if enable_insecure:
            warnings.warn("Insecure OAuth transport is enabled")
            os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        # Initialize the rest of the strategy
        super().__init__()

        # Ensure sessions are enabled
        if self._customs is not None:
            assert (
                self._customs.use_sessions
            ), f"{self.name.capitalize()} authentication requires sessions to be enabled"

    @property  # type: ignore
    @abstractmethod
    def name(self) -> str:
        ...  # pragma: no cover

    @name.setter  # type: ignore
    @abstractmethod
    def name(self, new_name: str):
        ...  # pragma: no cover

    @property  # type: ignore
    @abstractmethod
    def scopes(self) -> List[str]:
        ...  # pragma: no cover

    @scopes.setter  # type: ignore
    @abstractmethod
    def scopes(self, new_scopes: List[str]):
        ...  # pragma: no cover

    @property  # type: ignore
    @abstractmethod
    def authorization_base_url(self) -> str:
        ...  # pragma: no cover

    @authorization_base_url.setter  # type: ignore
    @abstractmethod
    def authorization_base_url(self, new_value: str):
        ...  # pragma: no cover

    @property  # type: ignore
    @abstractmethod
    def token_url(self) -> str:
        ...  # pragma: no cover

    @token_url.setter  # type: ignore
    @abstractmethod
    def token_url(self, new_value: str):
        ...  # pragma: no cover

    @property  # type: ignore
    @abstractmethod
    def user_profile_endpoint(self) -> str:
        ...  # pragma: no cover

    @user_profile_endpoint.setter  # type: ignore
    @abstractmethod
    def user_profile_endpoint(self, new_value: str):
        ...  # pragma: no cover

    @property  # type: ignore
    @abstractmethod
    def refresh_url(self) -> str:
        ...  # pragma: no cover

    @refresh_url.setter  # type: ignore
    @abstractmethod
    def refresh_url(self, new_value: str):
        ...  # pragma: no cover

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
            return client.get(self.user_profile_endpoint).json()

        except Exception:
            raise UnauthorizedException()

    def validate_token(self) -> Dict:
        """Method to validate a Github token with Github.

        Raises:
            UnauthorizedException: When the user isn't authenticated or token is not valid

        Returns:
            Dict: The data from the token
        """

        return {}

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        """Method to authenticate a user.

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
        """Register additional routes, specific for this strategy.

        Args:
            app (Flask): The app to register the strategies to
        """

        # Create a blueprint to register all related endpoints
        authentication_blueprint = Blueprint(
            self.name, __name__, url_prefix=self.endpoint_prefix
        )

        @authentication_blueprint.route("/login")
        def login():
            client = OAuth2Session(
                self.client_id,
                scope=self.scopes,
                redirect_uri=url_for(".callback", _external=True),
            )

            if self.name == "facebook":
                facebook_compliance_fix(client)

            authorization_url, state = client.authorization_url(
                self.authorization_base_url,
                access_type="offline",
                prompt="select_account",
            )

            # State is used to prevent CSRF, keep this for later.
            session["oauth_state"] = state
            return redirect(authorization_url)

        @authentication_blueprint.route("/callback", methods=["GET"])
        def callback():
            client = OAuth2Session(
                self.client_id,
                state=session["oauth_state"],
                redirect_uri=url_for(".callback", _external=True),
            )

            if self.name == "facebook":
                facebook_compliance_fix(client)

            self.token = client.fetch_token(
                self.token_url,
                client_secret=self.client_secret,
                authorization_response=request.url,
            )

            # Get additional data for the user
            user_data = self.get_user_info()

            # Ensure the user is registered
            user = self.get_or_create_user(user_data)

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
        app.register_blueprint(authentication_blueprint)
