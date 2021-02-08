from typing import Dict
from flask import Flask
from flask.json import jsonify

from customs import Customs
from customs.strategies import APIKeyStrategy
from customs.exceptions import UnauthorizedException

# Create the Flask app, and a secret for encrypting sessions
app = Flask(__name__)
app.secret_key = "541e8467-2321-4df9-8246-25b55dca3466"

# Create customs to protect the app, use sessions to keep users logged in across requests
customs = Customs(app, use_sessions=False)

# Mock database
DATABASE = {
    "4557F4F9-2CD3-4FAC-8C69-0C5540A8723F": {
        "Company": "Some company",
        "plan": "premium",
    }
}


class APIKeyAuthentication(APIKeyStrategy):
    def get_or_create_user(self, user: Dict):
        if user.get("key") in DATABASE:
            return DATABASE[user["key"]]
        else:
            raise UnauthorizedException()


# Create a strategy
api_key_strategy = APIKeyAuthentication()

# Declare the entire app a safe zone, all routes will be protected in the same way
customs.safe_zone(app, strategies=[api_key_strategy])


# ------------------ #
# Define some routes #
# ------------------ #


@app.route("/")
def index():
    return "Success"


@app.route("/test")
def test(user: Dict):
    return jsonify(user)


if __name__ == "__main__":
    app.run()
