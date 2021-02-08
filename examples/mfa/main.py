from base64 import b64encode
from customs.helpers import set_redirect_url

from typing import Any, Dict
from flask import Flask, Blueprint, request, session, render_template, redirect

from customs import Customs
from customs.strategies import LocalStrategy, AuthenticatorAppStrategy
from customs.exceptions import UnauthorizedException

from tinydb import TinyDB, Query


# Create the Flask app, and a secret for encrypting sessions
app = Flask(__name__)
app.secret_key = "541e8467-2321-4df9-8246-25b55dca3466"

# Create customs to protect the app, use sessions to keep users logged in across requests
customs = Customs(app, use_sessions=True, unauthorized_redirect_url="/login")

# Simple file based database
db = TinyDB("./db.json")
User = Query()


class LocalAuthentication(LocalStrategy):
    def get_or_create_user(self, user: Dict) -> Dict:
        record = db.get(User.username == user.get("username"))
        if record is not None:
            return record
        else:
            raise UnauthorizedException()

    def validate_credentials(self, username: str, password: str) -> Dict:
        record = db.get(User.username == username)
        if record is not None and record["password"] == password:
            return record
        else:
            raise UnauthorizedException()

    # def serialize_user(self, user: Any) -> Dict:
    #     return {"username": user.get("username")}

    # def deserialize_user(self, data: Dict) -> Any:
    #     username = data.get("username")
    #     user = db.get(User.username == username)
    #     return user


class AuthenticatorAppAuthentication(AuthenticatorAppStrategy):
    ...


# Create a strategy
local_strategy = LocalAuthentication()
authenticator_app_strategy = AuthenticatorAppAuthentication(not_verified_url="/enable_authenticator")

# Declare a part of the app as a safe zone, all routes will be protected in the same way
protected = customs.safe_zone(
    Blueprint("protected", __name__, url_prefix="/protected"),
    strategies=local_strategy,
    additional_strategies=authenticator_app_strategy,
)


# ------------------ #
# Define some routes #
# ------------------ #


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():
    set_redirect_url()
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Get the registration page
    if request.method == "GET":
        return render_template("register.html")

    # Submit the registration form
    else:

        # Get the form data
        username = request.form.get("username")
        password = request.form.get("password")
        repeat_password = request.form.get("repeat_password")

        # Basic checks
        if (
            username is not None
            and password is not None
            and password == repeat_password
            and len(username) > 3
            and len(password) > 3
        ):

            # Create the user in the database
            secret = authenticator_app_strategy.create_secret()
            user = {
                "username": username,
                "password": password,
                "totp_secret": secret,
                "totp_verified": False,
            }
            db.insert(user)

            serialized_user = local_strategy.serialize_user(user)
            session["user"] = serialized_user
            session["strategy"] = local_strategy.name

            # # Create a QR code for the user
            # qr_code = authenticator_app_strategy.create_qr_code(
            #     secret=secret, username=username, app_name="Example app"
            # )
            # qr_code = b64encode(qr_code.getvalue()).decode("ascii")

            # # Render the QR code for enabling the authenticator
            # return render_template("enable_authenticator.html", qr_code=qr_code)
            return redirect("/enable_authenticator")

        # Invalid registration
        else:
            return render_template("register.html", error="Fill all fields")


@app.route("/enable_authenticator", methods=["GET", "POST"])
@customs.protect(strategies=local_strategy)
def enable_authenticator(user: Dict):

    if request.method == "GET":

        # Create a QR code for the user and render it on the page
        qr_code = authenticator_app_strategy.create_qr_code(
            secret=user.get("totp_secret"),
            username=user.get("username"),
            app_name="Example app",
        )
        qr_code = b64encode(qr_code.getvalue()).decode("ascii")
        return render_template("enable_authenticator.html", qr_code=qr_code)

    elif request.method == "POST":

        otp = request.form.get("otp")
        print(user.get("totp_secret"), otp)
        if authenticator_app_strategy.verify(user.get("totp_secret"), otp):
            db.update({"totp_verified": True}, User.username == user.get("username"))
            return redirect("/")
        else:
            return redirect("/enable_authenticator")

    else:
        return redirect("/")


@protected.route("/authenticate", methods=["POST"])
def authenticate():
    return redirect("/")


@protected.route("/profile")
def profile(user: Dict):
    return render_template("profile.html", username=user.get("username"))


if __name__ == "__main__":
    app.register_blueprint(protected)
    app.run()
