import random
import string

from customs.strategies.basestrategy import BaseStrategy

from typing import Any, Callable, Dict, Optional, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_headers
from customs.exceptions import UnauthorizedException
from jose import jwt  # type: ignore


class JWTStrategy(BaseStrategy):

    name: str = "jwt"

    def __init__(self, authentication_function: Callable, key: Optional[str] = None, *args, **kwargs) -> None:
        if key is None:
            key = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
        self.key = key

        super().__init__(authentication_function, *args, **kwargs)

    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Dict[str, str]:

        # Parse the headers of the request
        headers = parse_headers(request)
        authorization_header = headers.get("authorization", "")

        if authorization_header.lower().startswith("bearer "):
            token = authorization_header[len("bearer "):]
            return {"token": token}

        return {}

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:

        # Get the token
        credentials = self.extract_credentials(request)
        token = credentials.get("token")
        if token is None:
            raise UnauthorizedException("No token found")

        # Decode and validate the token
        try:
            decoded = jwt.decode(token, self.key)
            return self.deserialize_user(decoded)

        except Exception as e:
            print(e)
            raise UnauthorizedException()

    def sign(self, user: Any) -> str:
        """ Sign a new token for the user. Serialize the user info before signing.

        Args:
            user (Any): The user data to serialize and sign

        Returns:
            str: The signed token
        """
        return jwt.encode(self.serialize_user(user), self.key)
