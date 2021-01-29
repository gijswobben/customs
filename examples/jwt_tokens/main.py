from typing import Dict
from flask import Flask, Blueprint
from flask.json import jsonify

from customs import Customs
from customs.strategies import BasicStrategy, JWTStrategy
from customs.exceptions import UnauthorizedException

# Create the Flask app
app = Flask(__name__)

# Create customs to protect the app, no need for sessions as we're using JWT tokens
customs = Customs(app, use_sessions=False)

# Mock database
DATABASE = {"admin": {"name": "Administrator User", "password": "admin"}}


def authentication_function(username: str, password: str) -> Dict:
    """Method that authenticates a user with a username and password

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
    """Method to serialize user information so it can be stored in a session.

    Args:
        user (Dict): The user information

    Returns:
        Dict: The serialized user information
    """
    return {"username": user.get("username")}


def deserialize_user(data: Dict) -> Dict:
    """Convert a serialized user (e.g. on a session cookie) back to the full
    user information.

    Args:
        data (Dict): The serialized user

    Returns:
        Dict: The full user information
    """
    return {"username": data.get("username"), **DATABASE[data.get("username")]}


# Create a strategies
basic_strategy = BasicStrategy(authentication_function)
jwt_strategy = JWTStrategy(
    authentication_function, key="9E30771F-6957-4C49-A8A0-55C292025349"
)

# Create a blueprint as a safe zone, protected using the JWT token strategy
api = customs.safe_zone(
    Blueprint("api", __name__, url_prefix="/api"), strategies=["jwt"]
)

# ----------------------- #
# Define some open routes #
# ----------------------- #


# Open to everyone
@app.route("/")
def index():
    return "Success"


# Use basic authentication to authenticate the user, create a token for subsequent calls
@app.route("/login", methods=["POST"])
@customs.protect(strategies=["basic"])
def login(user: Dict):
    token = jwt_strategy.sign(user)
    return jsonify({"token": token})


# ------------------------------ #
# Define some (protected) routes #
# ------------------------------ #


# Protected route, only available with a JWT token
@api.route("/user_info")
def user_info(user: Dict):
    user.pop("password")
    return jsonify(user)


if __name__ == "__main__":
    # Register the blueprint with the app
    app.register_blueprint(api)
    app.run()
