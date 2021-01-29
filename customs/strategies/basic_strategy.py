import base64

from customs.strategies.basestrategy import BaseStrategy
from customs.exceptions import UnauthorizedException

from typing import Any, Optional, Tuple, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_headers


class BasicStrategy(BaseStrategy):

    name: str = "basic"

    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Tuple[Optional[str], Optional[str]]:
        data = parse_headers(request)
        authorization_header = data.get("authorization", "")

        if authorization_header.lower().startswith("basic "):
            try:
                decoded = base64.b64decode(authorization_header[6:])
                username, password = decoded.decode("utf-8").split(":")
                return username, password
            except Exception as e:
                print(e)
                return None, None

        return None, None

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        username, password = self.extract_credentials(request)
        if username is None or password is None:
            raise UnauthorizedException()
        return self._authentication_function(username, password)
