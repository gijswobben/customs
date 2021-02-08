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
DATABASE: Dict[str, Dict] = {
    "admin": {"name": "Administrator User", "password": "admin"}
}


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


class JWTAuthentication(JWTStrategy):
    def get_or_create_user(self, user: Dict) -> Dict:
        if user.get("username") in DATABASE:
            return DATABASE[user["username"]]
        else:
            raise UnauthorizedException()


# Create a strategies
basic_strategy = BasicAuthentication()
jwt_strategy = JWTAuthentication(key="9E30771F-6957-4C49-A8A0-55C292025349")

# Create a blueprint as a safe zone, protected using the JWT token strategy
api = customs.safe_zone(
    Blueprint("api", __name__, url_prefix="/api"), strategies=[jwt_strategy]
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
@customs.protect(strategies=[basic_strategy])
def login(user: Dict):
    token = jwt_strategy.sign(user)
    return jsonify({"token": token})


# ------------------------------ #
# Define some (protected) routes #
# ------------------------------ #


# Protected route, only available with a JWT token
@api.route("/user_info")
def user_info(user: Dict):
    return jsonify({field: value for field, value in user.items() if field not in ["password"]})


if __name__ == "__main__":
    # Register the blueprint with the app
    app.register_blueprint(api)
    app.run()
