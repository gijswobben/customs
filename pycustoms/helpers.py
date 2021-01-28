import json

from typing import Dict, Union
from flask.wrappers import Request as FlaskRequest
from werkzeug.wrappers import Request


def parse_args(request: Union[Request, FlaskRequest]) -> Dict:
    try:
        return dict(request.args)
    except Exception:
        return {}


def parse_data(request: Union[Request, FlaskRequest]) -> Dict:
    try:
        return json.loads(request.data)
    except Exception:
        return {}


def parse_content(request: Union[Request, FlaskRequest]) -> Dict:
    return {**parse_args(request), **parse_data(request)}


def parse_headers(request: Union[Request, FlaskRequest]) -> Dict:
    return {str(key).lower(): value for key, value in dict(request.headers).items()}
