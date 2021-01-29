from abc import ABC, abstractclassmethod
from typing import Any, Callable, Dict, Optional, TypeVar, Union

from customs.customs import Customs
from flask import Request as FlaskRequest
from werkzeug.wrappers import Request

User = TypeVar("User")


class BaseStrategy(ABC):
    def __init__(
        self,
        authentication_function: Callable[[str, str], Dict],
        serialize_user_function: Optional[Callable] = None,
        deserialize_user_function: Optional[Callable] = None,
    ) -> None:

        # Store the authentication function (user provided)
        self._authentication_function = authentication_function

        # Store serialization/deserialization
        self._serialize_user_function = serialize_user_function
        self._deserialize_user_function = deserialize_user_function

        # Register this strategy as an available strategy for Customs
        customs = Customs()
        customs.register_strategy(self.name, self)

    @abstractclassmethod
    def extract_credentials(self, request: Union[Request, FlaskRequest]) -> Dict:
        ...

    @abstractclassmethod
    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        ...

    def serialize_user(self, user: User) -> Dict:
        if self._serialize_user_function is not None:
            return self._serialize_user_function(user)
        else:
            return user

    def deserialize_user(self, data: Dict) -> User:
        if self._deserialize_user_function is not None:
            return self._deserialize_user_function(data)
        else:
            return data
