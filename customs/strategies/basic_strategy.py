import base64

from customs.strategies.basestrategy import BaseStrategy
from customs.exceptions import UnauthorizedException

from typing import Any, Dict, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_headers


class BasicStrategy(BaseStrategy):

    name: str = "basic"

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

        # Extract the credentials
        credentials = self.extract_credentials(request)
        username = credentials.get("username")
        password = credentials.get("password")

        # Test authentication
        if username is None or password is None:
            raise UnauthorizedException()  # pragma: no cover
        return self._authentication_function(username, password)
