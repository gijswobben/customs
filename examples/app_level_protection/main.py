from typing import Dict
from flask import Flask
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

# Declare the entire app a safe zone, all routes will be protected in the same way
customs.safe_zone(app, strategies=[basic_strategy])


# ------------------ #
# Define some routes #
# ------------------ #


@app.route("/")
def index():
    return "Success"


@app.route("/user_info")
def user_info(user: Dict):
    user.pop("password")
    return jsonify(user)


if __name__ == "__main__":
    app.run()
