from flask.globals import request
import pytest
import base64

from flask import Flask
from typing import Dict
from customs import Customs
from customs.exceptions import UnauthorizedException
from customs.strategies import BasicStrategy


def test_basic_strategy_initialization_without_customs():
    class Basic(BasicStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    with pytest.warns(UserWarning):
        strategy = Basic()

    assert strategy.name == "basic"


def test_basic_strategy_initialization_with_customs():
    class Basic(BasicStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Basic()

    assert strategy.name == "basic"

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_basic_strategy_extract_crendentials():
    class Basic(BasicStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return super().get_or_create_user(user)

        def validate_credentials(self, username: str, password: str) -> Dict:
            return super().validate_credentials(username, password)

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Basic()

    with pytest.raises(UnauthorizedException):
        with app.test_request_context("/?test=123", json={"bla": "bla"}):
            strategy.extract_credentials(request)

    with pytest.raises(UnauthorizedException):
        with app.test_request_context("/", headers={"Authorization": "Basic test"}):
            strategy.extract_credentials(request)

    with app.test_request_context(
        "/",
        headers={
            "Authorization": "Basic %s"
            % base64.b64encode("test:test".encode()).decode()
        },
    ):
        credentials = strategy.extract_credentials(request)
        assert "username" in credentials
        assert "password" in credentials

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()


def test_basic_strategy_authenticate():
    class Basic(BasicStrategy):
        def get_or_create_user(self, user: Dict) -> Dict:
            return {}

        def validate_credentials(self, username: str, password: str) -> Dict:
            return {}

    # Create customs
    app = Flask("TESTS")
    app.secret_key = "630738a8-3b13-4311-8018-87554d6f7e85"
    Customs(app)

    # Create the strategy
    strategy = Basic()

    with app.test_request_context("/?test=123", json={"bla": "bla"}):

        with pytest.raises(UnauthorizedException):
            user = strategy.authenticate(request)

    with app.test_request_context(
        "/",
        headers={
            "Authorization": "Basic %s"
            % base64.b64encode("test:test".encode()).decode()
        },
    ):
        user = strategy.authenticate(request)
        assert user == {}

    # Cleanup of the Customs object used for testing
    Customs.remove_instance()
