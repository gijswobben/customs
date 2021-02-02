import warnings

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, Optional, Union

from flask.app import Flask

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request


class BaseStrategy(ABC):
    def __init__(
        self,
        serialize_user_function: Optional[Callable[[Any], Dict]] = None,
        deserialize_user_function: Optional[Callable[[Dict], Any]] = None,
    ) -> None:

        # Store serialization/deserialization
        self._serialize_user_function = serialize_user_function
        self._deserialize_user_function = deserialize_user_function

        # Register this strategy as an available strategy for Customs
        from customs.customs import Customs
        self._customs: Optional[Customs] = Customs.get_instance()
        if self._customs is not None:
            self._customs.register_strategy(self.name, self)
        else:
            warnings.warn("Unable to register strategy, make sure to initialize Customs first!")

    @property  # type: ignore
    @abstractmethod
    def name(self) -> str:
        ...  # pragma: no cover

    @name.setter  # type: ignore
    @abstractmethod
    def name(self, new_name: str):
        ...  # pragma: no cover

    @abstractmethod
    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Dict[str, str]:
        ...  # pragma: no cover

    @abstractmethod
    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        """ Method should return the user info """
        ...  # pragma: no cover

    @abstractmethod
    def get_or_create_user(self, user: Dict) -> Dict:
        ...  # pragma: no cover

    def serialize_user(self, user: Any) -> Dict:
        if self._serialize_user_function is not None:
            return self._serialize_user_function(user)
        else:
            if not isinstance(user, dict):
                return user.__dict__
            return user

    def deserialize_user(self, data: Dict) -> Any:
        if self._deserialize_user_function is not None:
            return self._deserialize_user_function(data)
        else:
            return data

    def register_additional_routes(self, app: Flask) -> None:
        ...
