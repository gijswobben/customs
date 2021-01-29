import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

if os.path.isfile("./VERSION"):
    with open("./VERSION") as fh:
        version = fh.read()
else:
    version = "master"


setuptools.setup(
    name="customs",
    version=version,
    author="NewInnovator",
    author_email="",
    license="MIT",
    description="Python library for guarding APIs.",
    keywords="Security Flask Authentication",
    url="https://github.com/gijswobben/customs",
    packages=setuptools.find_packages(),
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=["flask", "python-jose[cryptography]"],
    tests_require=["pytest", "pytest-cov"],
    python_requires=">=3.8",
    classifiers=[
        "Topic :: Utilities",
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
