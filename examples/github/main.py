import os

from typing import Any, Dict
from flask import Flask
from flask.templating import render_template

from customs import Customs
from customs.helpers import set_redirect_url
from customs.strategies import GithubStrategy
from customs.exceptions import UnauthorizedException


# App credentials for Github
client_id = os.environ.get("GITHUB_CLIENT_ID")
client_secret = os.environ.get("GITHUB_CLIENT_SECRET")

# Create the Flask app
app = Flask(__name__)
app.secret_key = "d2cc6f0a-0d9e-414c-a3ca-6b75455d6332"

# Create customs to protect the app, no need for sessions as we're using JWT tokens
customs = Customs(app, unauthorized_redirect_url="/login")

# Mock in-memory database (NOTE: Will forget everything on restart!)
DATABASE: Dict[str, Dict] = {}


# Create an implementation of the strategy (tell the strategy how to interact with our database for example)
class GithubAuthentication(GithubStrategy):

    scopes = ["user"]

    def get_or_create_user(self, user: Dict) -> Dict:

        user_id = str(user.get("id"))

        # Create the user if not in the database (so registration is open to everyone)
        if user_id not in DATABASE:
            DATABASE[user_id] = user

        # Return the user from the database
        return DATABASE[user_id]

    def serialize_user(self, user: Any) -> Dict:

        # Keep only the user ID on the session for speed and safety
        user_id = str(user.get("id"))
        return {"id": user_id}

    def deserialize_user(self, data: Dict) -> Any:

        # Get the user ID from the session
        user_id = str(data.get("id"))

        # Conver the ID back to the user data from the database
        if user_id is not None and user_id in DATABASE:
            return {"id": str(data.get("id")), **DATABASE[str(data.get("id"))]}
        else:
            raise UnauthorizedException()


# Create an instance of the strategy
github = GithubAuthentication(
    client_id=client_id,
    client_secret=client_secret,
    enable_insecure=True,  # For testing purposes only, don't use in production!
)

# ----------------------- #
# Define some open routes #
# ----------------------- #


# Open to everyone
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/login")
def login():

    # Store the URL of the page that redirected here and store
    # it so we can redirect to it after authentication
    set_redirect_url()
    return render_template("login.html")


# ------------------------------ #
# Define some (protected) routes #
# ------------------------------ #


@app.route("/profile")
@customs.protect(strategies=[github])
def profile(user: Dict):
    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run()
