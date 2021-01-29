from typing import Dict
from flask import Flask, Blueprint

from customs import Customs
from customs.strategies import LocalStrategy, BasicStrategy, JWTStrategy
from customs.exceptions import UnauthorizedException

app = Flask(__name__)
app.secret_key = "541e8467-2321-4df9-8246-25b55dca3466"

customs = Customs(app)

DATABASE = {"test": {"name": "Test User", "password": "test"}}


def authentication_function(username: str, password: str):
    if username in DATABASE and DATABASE[username].get("password", None) == password:
        return {"username": username, **DATABASE[username]}
    else:
        raise UnauthorizedException()


def serialize_user(user: Dict):
    return {"username": user.get("username")}


def deserialize_user(data):
    return {"username": data.get("username"), **DATABASE[data.get("username")]}


# Create some strategies
local_strategy = LocalStrategy(authentication_function)
basic_strategy = BasicStrategy(authentication_function)
jwt_strategy = JWTStrategy(
    serialize_user=serialize_user, deserialize_user=deserialize_user
)

# # Enable on all routes in the app
# customs.use("local", local_strategy)
# customs.use("basic", basic_strategy)

api = customs.safe_zone(
    Blueprint("api", __name__, url_prefix="/api"), strategies=["jwt"]
)


@app.route("/login", methods=["POST"])
@customs.protect(strategies=["local", "basic"])
def login(user: Dict):
    print(user)
    return jwt_strategy.sign(user)


@app.route("/")
@customs.ensure_authenticated
def index():
    return "Success"


@app.route("/test/<test>")
@customs.protect(strategies=["jwt"])
def test(test, *args, **kwargs):
    print(args, kwargs)
    return "Success"


@api.route("/test")
def root():
    return "Success"


@api.route("/test2")
def root2():
    return "Success"


if __name__ == "__main__":
    app.register_blueprint(api)
    app.run(debug=True)
