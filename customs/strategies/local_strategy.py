from abc import abstractmethod
from customs.exceptions import UnauthorizedException
from customs.strategies.base_strategy import BaseStrategy

from typing import Any, Dict, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_content


class LocalStrategy(BaseStrategy):
    """Authentication using request information (e.g. arguments) with username and password.
    """

    name: str = "local"

    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def validate_credentials(self, username: str, password: str) -> Dict:
        ...

    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:
        data = parse_content(request)
        try:
            return {"username": data["username"], "password": data["password"]}
        except Exception as e:
            print(e)
        return {}

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        credentials = self.extract_credentials(request)
        username = credentials.get("username")
        password = credentials.get("password")

        if username is None or password is None:
            raise UnauthorizedException()
        return self.validate_credentials(username, password)
