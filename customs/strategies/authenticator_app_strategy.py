from flask.app import Flask
from flask.blueprints import Blueprint
import io
import pyotp

from typing import Any, Dict, Union

from flask import Request as FlaskRequest
from werkzeug.wrappers import Request

from customs.helpers import parse_content, parse_headers
from customs.exceptions import UnauthorizedException
from customs.strategies.base_strategy import BaseStrategy

import pyqrcode
import png
from pyqrcode import QRCode


class AuthenticatorNotEnabledException(Exception):
    def __init__(self, target: str, *args: object) -> None:
        super().__init__(*args)
        self.target = target


class AuthenticatorAppStrategy(BaseStrategy):
    name = "authenticator_app"

    def __init__(self, not_verified_url: str) -> None:
        super().__init__()
        self.not_verified_url = not_verified_url

    def extract_credentials(
        self, request: Union[Request, FlaskRequest]
    ) -> Dict[str, str]:
        content = parse_content(request)
        headers = parse_headers(request)
        data = {**content, **headers}
        return {"otp": data.get("otp")}

    def authenticate(self, request: Union[Request, FlaskRequest], **kwargs) -> Any:

        # Make sure the first authentication already returned a user
        if "user" not in kwargs:
            raise UnauthorizedException()

        if kwargs["user"]["totp_verified"]:
            raise AuthenticatorNotEnabledException()

        # Extract the credentials from the request (OTP token)
        credentials = self.extract_credentials(request)

        # Get the TOTP secret for this user
        secret = kwargs["user"].get("totp_secret", None)
        if secret is None:
            # TOTP is not set up
            raise UnauthorizedException(target=self.not_verified_url)

        # Validate the OTP token
        totp = pyotp.TOTP(secret)
        if not totp.verify(credentials["otp"]):
            raise UnauthorizedException()

        # Return the original user
        return kwargs["user"]

    def get_or_create_user(self, user: Dict) -> Dict:
        # Second factor authentication doesn't have to retrieve the user
        return super().get_or_create_user(user)

    def create_qr_code(self, secret: str, username: str, app_name: str) -> io.BytesIO:

        totp = pyotp.TOTP(secret)
        url = pyqrcode.create(totp.provisioning_uri(name=username, issuer_name=app_name))

        f = io.BytesIO()
        url.png(f, scale=4)
        f.seek(0)
        return f

    def create_secret(self) -> str:
        return pyotp.random_base32()

    def verify(self, secret: str, otp: str) -> bool:
        totp = pyotp.TOTP(secret)
        return totp.verify(otp)
