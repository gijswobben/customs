from __future__ import annotations

import inspect
import warnings

from datetime import timedelta
from flask import Flask, Blueprint, request, session
from customs.exceptions import HTTPException

from types import MethodType
from typing import (
    Callable,
    Dict,
    List,
    TYPE_CHECKING,
    Any,
    Optional,
    T,
    Type,
    TypeVar,
    Union,
)

if TYPE_CHECKING:
    from customs.strategies.basestrategy import BaseStrategy
    from wsgiref.types import StartResponse
    from flask.wrappers import Request


User = TypeVar("User")


class _Singleton(type):
    """Metaclass for defining classes that should match the singleton
    pattern, meaning there can only be a single instance of the class.

    Args:
        cls (Type[T]): The class to instantiate (or retrieve)

    Returns:
        T: Instance of class T
    """

    _instances = {}

    def __call__(cls: Type[T], *args, **kwargs) -> T:
        if cls not in cls._instances:
            cls._instances[cls] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def get_instance(cls: Type[T]) -> Optional[T]:
        """Get an existing instance of class T, if it exists. Returns None if no
        instance exists.

        Args:
            cls (Type[T]): The type of instance to retrieve

        Returns:
            Optional[T]: The instance
        """
        if cls not in cls._instances:
            return None
        return cls._instances[cls]


class Customs(metaclass=_Singleton):
    """Customs is a protective layer that makes sure every incoming request is properly
    authenticated and checked. Customs can define "safe zones", like parts of your API, or
    protect individual routes.

    Args:
        app (Flask): The Flask application to mount this middleware on
        use_sessions (bool, optional): Whether or not to use sessions for storing user information. Defaults to True.
        session_timeout (timedelta, optional): The default expiration time for sessions. Defaults to timedelta(days=31).
        user_class (Type, optional): The class to use for parsing user information. Defaults to dict.
    """

    def __init__(
        self,
        app: Flask,
        use_sessions: bool = True,
        session_timeout: timedelta = timedelta(days=31),
        user_class: Type = dict,
    ) -> None:

        # Make sure the user has set a secret
        assert (
            app.secret_key is not None
        ), "App secret is required for using sessions, sessions will be disabled."

        # Store the original WSGI app
        self.app = app
        self.wsgi_app = app.wsgi_app

        # Replace the app's WSGI app with this middleware
        app.wsgi_app = self

        # Store input arguments
        self.use_sessions = use_sessions
        self.user_class = user_class

        # Define placeholders for the strategies in use, and registered available strategies
        self.strategies: Dict[str, BaseStrategy] = {}
        self.available_strategies: Dict[str, BaseStrategy] = {}

        # Make sessions timeout
        self.app.permanent_session_lifetime = session_timeout

        # Register the before_request handler which will check every request using the specified strategies
        self.app.before_request(self._before_request)

    def _xray_request(self):
        ...
        # TODO: Implement checks on the request

    def _check_passport(self) -> User:
        ...

    def _check_authorization(self):
        ...

    def _grant_access(self, user: User):

        # Get the view_function that the user wants access to
        view_function = self.app.view_functions.get(request.url_rule.endpoint)
        assert view_function is not None, "View function not found"

        # Add the user as argument to the view function (but only if it accepts it)
        view_function_has_kwargs = any(
            [
                parameter.kind == inspect.Parameter.VAR_KEYWORD
                for parameter in list(
                    dict(inspect.signature(view_function).parameters).values()
                )
            ]
        )
        if (
            "user" in inspect.signature(view_function).parameters
            or view_function_has_kwargs
        ):
            request.view_args["user"] = user

    def _before_request(self):
        """Method that runs before every request. Should check the request using
        the defined strategies that are in use. Will add the found user to the arguments
        of the user defined request handler.
        """

        # 1: X-ray the request to find tokens/sessions/... (raise exceptions when needed)
        # self._xray_request()

        # 2: Check the identity/passport of the user (return identity)
        user = self._check_passport()

        # 3: Check authorization
        # self._check_authorization()

        # 4: Handle view function
        self._grant_access(user=user)

        # # Don't do anything if no strategies are in use
        # if len(self.strategies.values()) != 0:

        #     if not self.is_authenticated():

        #         # Get the function that will handle the request (user defined)
        #         request_handler = self.app.view_functions.get(request.url_rule.endpoint)
        #         try:

        #             # Verify the request and extract the user
        #             user = self._verify_request(request, self.strategies.values())

        #             # Add the user as argument to the handler function (but only if it accepts it)
        #             request_handler_has_kwargs = any(
        #                 [
        #                     parameter.kind == inspect.Parameter.VAR_KEYWORD
        #                     for parameter in list(
        #                         dict(
        #                             inspect.signature(request_handler).parameters
        #                         ).values()
        #                     )
        #                 ]
        #             )
        #             if (
        #                 "user" in inspect.signature(request_handler).parameters
        #                 or request_handler_has_kwargs
        #             ):
        #                 request.view_args["user"] = user

        #         except HTTPException as e:
        #             return e.message, e.status_code

    def register_strategy(self, name: str, strategy: BaseStrategy) -> Customs:
        """Register a strategy without using it for every route. Makes the strategy
        available by its name.

        Args:
            name (str): The name of the strategy
            strategy (BaseStrategy): The strategy (which should inherit from BaseStrategy)

        Returns:
            Customs: Returns this instance of customs for chaining
        """
        # Store the strategy
        self.available_strategies[name] = strategy
        return self

    def is_authenticated(self) -> bool:
        return session.get("is_authenticated", False)

    def ensure_authenticated(self, func: Callable) -> Callable:
        """Decorator method that wraps a view function so it can only be accessed by
        authenticated users.

        Args:
            func (Callable): The function to decorate

        Returns:
            Callable: The decorated function
        """

        def wrapper(*args, **kwargs):
            if self.is_authenticated():
                return func(*args, **kwargs)
            else:
                return "Unauthorized", 401

        wrapper.__name__ = func.__name__
        return wrapper

    def protect(self, strategies: Union[List[str], str]) -> Callable:
        """Decorator method that protects a specific route, using a set of strategies.

        Args:
            strategies (Union[List[str], str]): The strategy or list of strategies to use for protection

        Returns:
            Callable: The wrapped view function
        """

        # Make sure we have a list of strategies
        if not isinstance(
            strategies,
            (
                list,
                tuple,
            ),
        ):
            strategies = [strategies]

        # Convert the names of strategies back to strategy objects
        strategy_objects: List[BaseStrategy] = []
        for strategy_name in strategies:
            strategy = self.available_strategies.get(strategy_name)
            if strategy is None:
                warnings.warn(
                    f"No strategy named '{strategy}' registered in Customs."
                    f"Available strategies are: {', '.join(self.available_strategies.keys())}"
                )
            else:
                strategy_objects.append(strategy)

        def func_wrapper(func: Callable) -> Callable:
            def wrapper(*args, **kwargs):

                if not self.is_authenticated():

                    # Mark session as permanent to enforce the timeout
                    session.permanent = True

                    exceptions = []
                    for strategy in strategy_objects:
                        try:

                            # Use the strategy to authenticate the request and retrieve the user
                            user = strategy.authenticate(request)

                            # Store the user on the session cookie
                            if self.use_sessions:
                                session["user"] = user
                                session["is_authenticated"] = True

                            # Add the user as argument to the handler function
                            if "user" in inspect.signature(func).parameters:
                                kwargs["user"] = user

                            return func(*args, **kwargs)

                        # Catch all exceptions
                        except Exception as e:
                            exceptions.append(e)

                    # Return the first exception if no strategy was successful
                    return exceptions[0].message, exceptions[0].status_code

                else:
                    # TODO: Deserialize user
                    return func(*args, **kwargs)

            # Update the wrapper name before returning
            wrapper.__name__ = func.__name__
            return wrapper

        return func_wrapper

    def _verify_request(
        self, current_request: Request, strategies: List[BaseStrategy]
    ) -> Any:

        # TODO: Deserialize user if the request was already authenticated

        # Keep track of exceptions that are thrown by the different strategies
        exceptions: List[Exception] = []

        # Loop the set of strategies
        for strategy in strategies:

            # Authenticate using the strategies "authenticate" method
            try:
                user = strategy.authenticate(current_request)

                # Try to convert the user data when the type isn't correct
                if not isinstance(user, self.user_class):
                    user = self.user_class(user)

                # Store the user on the session cookie
                if self.use_sessions:
                    session["user"] = user
                    session["is_authenticated"] = True

                # Return the user
                return user

            except HTTPException as e:
                exceptions.append(e)

        # Raise the exception from the first strategy if none of them worked
        raise exceptions[0]

    def safe_zone(self, zone: Union[Blueprint, Flask], strategies: List[str]):
        """Create a zone/section of the app that is protected with specific strategies. The
        zone can be an entire Flask application, or a section of the app in the form of a Blueprint.

        Args:
            zone (Union[Blueprint, Flask]): The zone to protect
            strategies (List[str]): The names of the strategies to use

        Returns:
            Union[Blueprint, Flask]: The (now protected) input zone
        """

        # Protect all endpoints in a blueprint
        if isinstance(zone, Blueprint):

            def _add_url_rule(_self, rule, endpoint=None, view_func=None, **options):
                """Like :meth:`Flask.add_url_rule` but for a blueprint.  The endpoint for
                the :func:`url_for` function is prefixed with the name of the blueprint.
                """
                if endpoint:
                    assert (
                        "." not in endpoint
                    ), "Blueprint endpoints should not contain dots"
                if view_func and hasattr(view_func, "__name__"):
                    # Protect (wrap) the view_func with the strategies
                    view_func = self.protect(strategies=strategies)(view_func)
                    assert (
                        "." not in view_func.__name__
                    ), "Blueprint view function name should not contain dots"
                _self.record(
                    lambda s: s.add_url_rule(rule, endpoint, view_func, **options)
                )

            # Patch the blueprint with a new add_url_rule method, which will wrap the route with protection
            zone.add_url_rule = MethodType(_add_url_rule, zone)
            return zone

        # Protect an entire app
        elif isinstance(zone, Flask):

            # Loop the listed strategies
            for strategy in strategies:

                # Get the strategy from the available strategies
                strategy_object = self.available_strategies.get(strategy)
                if strategy_object is None:
                    warnings.warn(
                        f"Strategy '{strategy}' is not registered with Customs and will be ignored"
                    )
                else:
                    self.strategies[strategy] = strategy_object

            return zone

    def __call__(self, environ: Dict, start_response: StartResponse) -> Any:
        # Call the original WSGI app (without modifications)
        return self.wsgi_app(environ, start_response)


# X-ray
# Clearance
# Declaration
# Stamps
# Passport
# Duty free
# Terminal/Gate
