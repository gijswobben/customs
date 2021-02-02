from customs.helpers import (
    parse_args,
    parse_content,
    parse_headers,
    parse_data,
    set_redirect_url,
)

from flask import Flask, request, session


def test_parse_args():

    # Create a test app
    app = Flask(__name__)

    with app.test_request_context("/?test=123"):
        args = parse_args(request)
        assert "test" in args and args["test"] == "123"


def test_parse_content():

    # Create a test app
    app = Flask(__name__)

    with app.test_request_context("/?test=123", json={"bla": "bla"}):
        content = parse_content(request)
        assert "test" in content and content["test"] == "123"
        assert "bla" in content and content["bla"] == "bla"


def test_parse_headers():

    # Create a test app
    app = Flask(__name__)

    with app.test_request_context("/", headers={"User-Agent": "Your value"}):
        headers = parse_headers(request)
        print(headers)
        assert "user-agent" in headers and headers["user-agent"] == "Your value"


def test_parse_data():

    # Create a test app
    app = Flask(__name__)

    with app.test_request_context("/", json={"bla": "bla"}):
        data = parse_data(request)
        assert "bla" in data and data["bla"] == "bla"

    with app.test_request_context("/", data="some-data-string"):
        data = parse_data(request)
        assert data == {}


def test_set_redirect_url():

    # Create a test app
    app = Flask(__name__)
    app.secret_key = "bcdec7a5-f9fc-48db-8a11-1fefe7a7c809"

    with app.test_request_context("/?next=test"):
        set_redirect_url()
        assert session["next"] == "test"
