from customs.strategies.basestrategy import BaseStrategy

from typing import Any, Optional, Tuple, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request
from customs.helpers import parse_content


class LocalStrategy(BaseStrategy):

    name: str = "local"

    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Tuple[Optional[str], Optional[str]]:
        data = parse_content(request)
        return data.get("username"), data.get("password")

    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        username, password = self.extract_credentials(request)
        return self._authentication_function(username, password)
