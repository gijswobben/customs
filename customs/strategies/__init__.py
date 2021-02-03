"""Strategies define how the customs should protect a resource (endpoint, blueprint, or app). Strategies can
be combined to create the desired protection. Strategies should be subclassed to tell them about application
specific element, for example how to read a user from the database.
"""

from customs.strategies.local_strategy import LocalStrategy
from customs.strategies.basic_strategy import BasicStrategy
from customs.strategies.jwt_strategy import JWTStrategy
from customs.strategies.google_strategy import GoogleStrategy
from customs.strategies.github_strategy import GithubStrategy
from customs.strategies.facebook_strategy import FacebookStrategy


__all__ = ["LocalStrategy", "BasicStrategy", "JWTStrategy", "GoogleStrategy", "GithubStrategy", "FacebookStrategy"]
