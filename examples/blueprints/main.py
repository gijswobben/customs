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


class BasicAuthentication(BasicStrategy):
    def get_or_create_user(self, user: Dict) -> Dict:
        if user.get("username") in DATABASE:
            return DATABASE[user["username"]]
        else:
            raise UnauthorizedException()

    def validate_credentials(self, username: str, password: str) -> Dict:
        if username in DATABASE and DATABASE[username].get("password") == password:
            return DATABASE[username]
        else:
            raise UnauthorizedException()


# Create a strategy
basic_strategy = BasicAuthentication()

# Create a blueprint as a safe zone
secure = customs.safe_zone(
    Blueprint("secure", __name__, url_prefix="/secure"), strategies=[basic_strategy]
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
    return jsonify({field: value for field, value in user.items() if field not in ["password"]})


if __name__ == "__main__":
    # Register the blueprint with the app
    app.register_blueprint(secure)
    app.run()
