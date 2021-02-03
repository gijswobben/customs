import base64

from typing import Any, Dict, Union

from abc import abstractmethod
from flask import Request as FlaskRequest
from werkzeug.wrappers import Request

from customs.helpers import parse_headers
from customs.exceptions import UnauthorizedException
from customs.strategies.base_strategy import BaseStrategy


class BasicStrategy(BaseStrategy):
    """Strategy that enables authorization using the "basic" authorization header.

    Examples:
        >>> class BasicAuthentication(BasicStrategy):
        ...     def get_or_create_user(self, user: Dict) -> Dict:
        ...         if user.get("username") in DATABASE:
        ...             return DATABASE[user["username"]]
        ...         else:
        ...             raise UnauthorizedException()
        ...     def validate_credentials(self, username: str, password: str) -> Dict:
        ...         if username in DATABASE and DATABASE[username].get("password") == password:
        ...             return DATABASE[username]
        ...         else:
        ...             raise UnauthorizedException()
    """

    name: str = "basic"

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def validate_credentials(self, username: str, password: str) -> Dict:
        ...  # pragma: no cover

    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:

        # Parse the headers of the request
        headers = parse_headers(request)
        authorization_header = headers.get("authorization", "")

        if authorization_header.lower().startswith("basic "):
            try:
                decoded = base64.b64decode(authorization_header[len("basic "):])
                username, password = decoded.decode("utf-8").split(":")
                return {"username": username, "password": password}
            except Exception as e:
                print(e)
                raise UnauthorizedException()

        else:
            raise UnauthorizedException()

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        """Method that will extract the basic authorization header from the request,
        and will then call the `validate_credentials` method with a username and password.
        The `validate_credentials` method should be implemented by the user. This method is called
        by Customs internally and is not intended for external use.

        Args:
            request (Union[Request, FlaskRequest]): The incoming request (usually a Flask request)

        Raises:
            UnauthorizedException: Raised when the user is not authorized (invalid or missing credentials)

        Returns:
            Dict: The user information
        """

        # Extract the credentials
        credentials = self.extract_credentials(request)
        username = credentials.get("username")
        password = credentials.get("password")

        # Test authentication
        if username is None or password is None:
            raise UnauthorizedException()  # pragma: no cover
        return self.validate_credentials(username, password)
