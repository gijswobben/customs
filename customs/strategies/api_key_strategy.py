from typing import Any, Dict, Union

from werkzeug.wrappers import Request
from flask.wrappers import Request as FlaskRequest

from customs.helpers import parse_content, parse_headers
from customs.exceptions import UnauthorizedException
from customs.strategies.base_strategy import BaseStrategy


class APIKeyStrategy(BaseStrategy):
    name = "api_key"

    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:
        data = parse_content(request)
        headers = parse_headers(request)

        if "key" in headers:
            return {"key": headers["key"]}
        elif "key" in data:
            return {"key": data["key"]}
        else:
            return {}

    def authenticate(self, request: Union[Request, FlaskRequest], **kwargs) -> Any:
        credentials = self.extract_credentials(request)

        if credentials.get("key") is None:
            raise UnauthorizedException()
        return self.get_or_create_user(credentials)
