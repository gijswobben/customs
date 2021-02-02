import json

from typing import Dict, Union
from flask import request, session
from flask.wrappers import Request as FlaskRequest
from werkzeug.wrappers import Request


def parse_args(request: Union[Request, FlaskRequest]) -> Dict:
    return dict(request.args)


def parse_data(request: Union[Request, FlaskRequest]) -> Dict:
    try:
        return json.loads(request.data)
    except Exception:
        return {}


def parse_content(request: Union[Request, FlaskRequest]) -> Dict:
    return {**parse_args(request), **parse_data(request)}


def parse_headers(request: Union[Request, FlaskRequest]) -> Dict:
    return {str(key).lower(): value for key, value in dict(request.headers).items()}


def set_redirect_url():

    # Get the URL of the page that got us here
    if request.args.get("next") is not None:
        session["next"] = request.args.get("next")
