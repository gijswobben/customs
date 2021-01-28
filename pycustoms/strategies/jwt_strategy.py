from pycustoms.strategies.basestrategy import BaseStrategy

from typing import Any, Callable, Dict, Optional, Tuple, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from pycustoms.helpers import parse_headers
from pycustoms.exceptions import UnauthorizedException
from jose import jwt


class JWTStrategy(BaseStrategy):

    name: str = "jwt"
    key: str = "88cbf57a-7d0b-4f1e-a8d2-a7d4db8adb04"

    def __init__(self, serialize_user, deserialize_user) -> None:
        authentication_function = lambda x: ...
        self.serialize_user = serialize_user
        self.deserialize_user = deserialize_user
        super().__init__(authentication_function)

    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Optional[str]:
        data = parse_headers(request)
        authorization_header = data.get("authorization", "")

        if authorization_header.lower().startswith("bearer "):
            token = authorization_header[len("bearer "):]
            return token
        else:
            return None

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:

        # Get the token
        token = self.extract_credentials(request)
        if token is None:
            raise UnauthorizedException("No token found")

        # Decode and validate the token
        try:
            decoded = jwt.decode(token, self.key)
            self.deserialize_user(decoded)
        except Exception as e:
            print(e)
            raise

    def sign(self, user: Any) -> str:
        return jwt.encode(self.serialize_user(user), self.key)
