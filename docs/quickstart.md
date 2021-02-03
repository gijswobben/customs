# Quickstart
Getting started with Customs is easy, just install Customs, configure an authentication strategy and start protecting your endpoints. In this quickstart guid we'll set up basic authentication to protect a specific route. Check out the rest of the docs and examples to see all possibilities.

__1. Install Customs__

Install the package using `pip`:

```shell
$ pip install customs
```

__2. Configure a strategy__

Pick a base strategy to work from, in this case the `BasicStrategy`. This strategy will automatically check the `Authorization` header in the request and look for base64 encoded credentials. All we got to do here is tell the strategy how to check the username and password and how to get user information from a username.

```python
class BasicAuthentication(BasicStrategy):
    def validate_credentials(self, username: str, password: str) -> Dict:
        """ Method to validate credentials (username and password).
        """

        # If the user is in the database and the password is correct
        if username in DATABASE and DATABASE[username].get("password") == password:
            return DATABASE[username]

        # Otherwise raise an exception
        else:
            raise UnauthorizedException()

    def get_or_create_user(self, user: Dict) -> Dict:
        """ Method to get user information from the database (or optionally create the user in the database).
        """

        # If the user exists in our database, return the information
        if user.get("username") in DATABASE:
            return DATABASE[user["username"]]

        # If the username is not in the database, raise an exception
        else:
            raise UnauthorizedException()
```

As you can see we've created a subclass of the `BasicStrategy` and we've created methods that tell the strategy how to interact with the database. That's it!

__3. Protect your app__

Now we're ready to use the strategy to protect an application. To so do, we start with a `Customs` object which will `protect` our endpoints or creates a `safe_zone` for a set of endpoints. Lets stick with a single endpoint for now.

```python
from flask import Flask
from customs import Customs

# Create the app, and the customs
app = Flask(__name__)
customs = Customs(app)

# ... The strategy definition we've created before goes here

# Make an instance of our basic authentication strategy
basic_authentication = BasicAuthentication()

@app.route("/")
def index():
    return "This is an open route, everyone has access"

@app.route("/protected")
@customs.protect(strategies=[basic_authentication])
def protected():
    return "This is a protected route, users only!"
```

This app now has 2 routes. One is open to the world (http://localhost:5000/) and one is protected with basic authentication (http://localhost:5000/protected).

For full examples head over to the `examples/` directory.
