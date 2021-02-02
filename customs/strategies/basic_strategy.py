import base64

from typing import Any, Dict, Union

from abc import ABC, abstractmethod
from flask import Request as FlaskRequest
from werkzeug.wrappers import Request

from customs.helpers import parse_headers
from customs.exceptions import UnauthorizedException
from customs.strategies.basestrategy import BaseStrategy


class BasicStrategy(BaseStrategy, ABC):

    name: str = "basic"

    def __init__(self) -> None:
        super().__init__(
            serialize_user_function=None,
            deserialize_user_function=None,
        )

    @abstractmethod
    def validate_credentials(self, username: str, password: str) -> Dict:
        ...

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
        return self.validate_credentials(username, password)
