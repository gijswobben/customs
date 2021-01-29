from flask.globals import request
import pytest

from flask import Flask
from typing import Dict
from customs import Customs
from customs.exceptions import UnauthorizedException
from customs.strategies import JWTStrategy


def test_jwt_strategy_initialization_without_customs():
    def authentication_function(username: str, password: str) -> Dict:
        return {}

    with pytest.warns(UserWarning):
        strategy = JWTStrategy(authentication_function)

    assert strategy.name == "jwt"


def test_jwt_strategy_initialization_with_customs():
    def authentication_function(username: str, password: str) -> Dict:
        return {}

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = JWTStrategy(authentication_function)

    assert strategy.name == "jwt"

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_jwt_strategy_extract_crendentials():
    def authentication_function(username: str, password: str) -> Dict:
        return {}

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = JWTStrategy(authentication_function)

    with app.test_request_context("/?test=123", json={"bla": "bla"}):
        credentials = strategy.extract_credentials(request)
        assert credentials == {}

    test_user = {}
    token = strategy.sign(test_user)

    with app.test_request_context("/", headers={"Authorization": f"Bearer {token}"}):
        credentials = strategy.extract_credentials(request)
        assert "token" in credentials

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_jwt_strategy_authenticate():
    def authentication_function(username: str, password: str) -> Dict:
        if username == "test" and password == "test":
            return {}
        else:
            raise UnauthorizedException()

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = JWTStrategy(authentication_function)

    with app.test_request_context("/?test=123", json={"bla": "bla"}):

        with pytest.raises(UnauthorizedException):
            user = strategy.authenticate(request)

    test_user = {}
    token = strategy.sign(test_user)

    with app.test_request_context("/", headers={"Authorization": f"Bearer {token}"}):
        user = strategy.authenticate(request)
        assert user == {}

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_jwt_strategy_authenticate_invalid_token():
    def authentication_function(username: str, password: str) -> Dict:
        if username == "test" and password == "test":
            return {}
        else:
            raise UnauthorizedException()

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = JWTStrategy(authentication_function)

    with app.test_request_context("/?test=123", json={"bla": "bla"}):

        with pytest.raises(UnauthorizedException):
            strategy.authenticate(request)

    with pytest.raises(UnauthorizedException):
        with app.test_request_context("/", headers={"Authorization": "Bearer test"}):
            strategy.authenticate(request)

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()
