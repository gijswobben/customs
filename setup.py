from setuptools import setup
from setuptools import find_packages


setup(
    name="customs",
    version="0.1.0",
    author="NewInnovator",
    author_email="",
    description=("Python library for guarding APIs."),
    keywords="",
    url="",
    packages=find_packages(),
    long_description_content_type="text/markdown",
    long_description="",
    install_requires=[
        "python-jose[cryptography]"
    ]
)