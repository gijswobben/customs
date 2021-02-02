from flask.globals import request
import pytest

from flask import Flask
from typing import Dict
from customs import Customs
from customs.exceptions import UnauthorizedException
from customs.strategies import LocalStrategy


def test_local_strategy_initialization_without_customs():
    class Local(LocalStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    with pytest.warns(UserWarning):
        print(Customs.get_instance())
        strategy = Local()

    assert strategy.name == "local"


def test_local_strategy_initialization_with_customs():
    class Local(LocalStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Local()

    assert strategy.name == "local"

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_local_strategy_extract_crendentials():
    class Local(LocalStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Local()

    with app.test_request_context("/?test=123", json={"bla": "bla"}):
        credentials = strategy.extract_credentials(request)
        assert credentials == {}

    with app.test_request_context("/?username=test&password=test"):
        credentials = strategy.extract_credentials(request)
        assert "username" in credentials
        assert "password" in credentials

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_local_strategy_authenticate():
    class Local(LocalStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return {}

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Local()

    with app.test_request_context("/?test=123", json={"bla": "bla"}):

        with pytest.raises(UnauthorizedException):
            user = strategy.authenticate(request)

    with app.test_request_context("/?username=test&password=test"):
        user = strategy.authenticate(request)
        assert user == {}

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()
