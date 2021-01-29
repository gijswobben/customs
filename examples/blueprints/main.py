from typing import Dict
from flask import Flask, Blueprint
from flask.json import jsonify

from customs import Customs
from customs.strategies import BasicStrategy
from customs.exceptions import UnauthorizedException

# Create the Flask app, and a secret for encrypting sessions
app = Flask(__name__)
app.secret_key = "541e8467-2321-4df9-8246-25b55dca3466"

# Create customs to protect the app, use sessions to keep users logged in across requests
customs = Customs(app, use_sessions=True)

# Mock database
DATABASE = {"admin": {"name": "Administrator User", "password": "admin"}}


def authentication_function(username: str, password: str) -> Dict:
    """ Method that authenticates a user with a username and password

    Args:
        username (str): The username
        password (str): The password

    Raises:
        UnauthorizedException: Thrown when the user could not be authenticated

    Returns:
        Dict: The user information
    """
    # Look up the user and test the password
    if username in DATABASE and DATABASE[username].get("password", None) == password:
        return {"username": username, **DATABASE[username]}
    else:
        raise UnauthorizedException()


def serialize_user(user: Dict) -> Dict:
    """ Method to serialize user information so it can be stored in a session.

    Args:
        user (Dict): The user information

    Returns:
        Dict: The serialized user information
    """
    return {"username": user.get("username")}


def deserialize_user(data: Dict) -> Dict:
    """ Convert a serialized user (e.g. on a session cookie) back to the full
    user information.

    Args:
        data (Dict): The serialized user

    Returns:
        Dict: The full user information
    """
    return {"username": data.get("username"), **DATABASE[data.get("username")]}


# Create a strategy
basic_strategy = BasicStrategy(authentication_function)

# Create a blueprint as a safe zone
secure = customs.safe_zone(
    Blueprint("secure", __name__, url_prefix="/secure"), strategies=["basic"]
)

# ----------------------- #
# Define some open routes #
# ----------------------- #


@app.route("/")
def index():
    return "Success"


# ------------------------------ #
# Define some (protected) routes #
# ------------------------------ #


@secure.route("/test")
def test():
    return "Success"


@secure.route("/user_info")
def user_info(user: Dict):
    user.pop("password")
    return jsonify(user)


if __name__ == "__main__":
    # Register the blueprint with the app
    app.register_blueprint(secure)
    app.run()
