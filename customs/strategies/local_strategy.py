from customs.exceptions import UnauthorizedException
from customs.strategies.basestrategy import BaseStrategy

from typing import Any, Dict, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_content


class LocalStrategy(BaseStrategy):

    name: str = "local"

    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Dict[str, str]:
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
        return self._authentication_function(username, password)
