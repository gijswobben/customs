from abc import ABC, abstractclassmethod
from typing import Any, Callable, Dict, Union

from pycustoms.pycustoms import Customs
from flask import Request as FlaskRequest
from werkzeug.wrappers import Request


class BaseStrategy(ABC):
    def __init__(self, authentication_function: Callable[[str, str], Dict]) -> None:

        # Store the authentication function (user provided)
        self._authentication_function = authentication_function

        # Register this strategy as an available strategy for Customs
        customs = Customs()
        customs.register_strategy(self.name, self)

    @abstractclassmethod
    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Dict:
        ...

    @abstractclassmethod
    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        ...

