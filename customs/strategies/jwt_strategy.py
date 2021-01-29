from customs.strategies.basestrategy import BaseStrategy

from typing import Any, Optional, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_headers
from customs.exceptions import UnauthorizedException
from jose import jwt


class JWTStrategy(BaseStrategy):

    name: str = "jwt"
    key: str = "88cbf57a-7d0b-4f1e-a8d2-a7d4db8adb04"  # TODO: Move to argument

    def __init__(self, serialize_user, deserialize_user) -> None:
        self._serialize_user_function = serialize_user
        self._deserialize_user_function = deserialize_user
        super().__init__()

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
            return self.deserialize_user(decoded)
        except Exception as e:
            print(e)
            raise

    def sign(self, user: Any) -> str:
        return jwt.encode(self.serialize_user(user), self.key)
