import os
import sys

from typing import Dict
from flask import Flask
from flask.templating import render_template

from customs import Customs
from customs.helpers import set_redirect_url


# Create the Flask app
app = Flask(__name__)
app.secret_key = "d2cc6f0a-0d9e-414c-a3ca-6b75455d6332"

# Create customs to protect the app, no need for sessions as we're using JWT tokens
customs = Customs(app, unauthorized_redirect_url="/login")

# Mock in-memory database (NOTE: Will forget everything on restart!)
DATABASE: Dict[str, Dict] = {}

# Import strategies from other examples
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.main import google  # noqa
from github.main import github  # noqa


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
@customs.protect(strategies=[github, google])
def profile(user: Dict):
    return render_template("profile.html", user=user)


if __name__ == "__main__":
    app.run()
