import warnings

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union

from flask.app import Flask

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request


class BaseStrategy(ABC):
    def __init__(
        self,
    ) -> None:

        # Register this strategy as an available strategy for Customs
        from customs.customs import Customs

        self._customs: Optional[Customs] = Customs.get_instance()
        if self._customs is not None:
            self._customs.register_strategy(self.name, self)
        else:
            warnings.warn(
                "Unable to register strategy, make sure to initialize Customs first!"
            )

    @property  # type: ignore
    @abstractmethod
    def name(self) -> str:
        ...  # pragma: no cover

    @name.setter  # type: ignore
    @abstractmethod
    def name(self, new_name: str):
        ...  # pragma: no cover

    @abstractmethod
    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:
        ...  # pragma: no cover

    @abstractmethod
    def authenticate(self, request: Union[Request, FlaskRequest]) -> Any:
        """ Method should return the user info """
        ...  # pragma: no cover

    @abstractmethod
    def get_or_create_user(self, user: Dict) -> Dict:
        ...  # pragma: no cover

    def serialize_user(self, user: Any) -> Dict:
        return user

    def deserialize_user(self, data: Dict) -> Any:
        return data

    def register_additional_routes(self, app: Flask) -> None:
        ...
