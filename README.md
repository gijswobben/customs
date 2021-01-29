![Tests](https://img.shields.io/github/workflow/status/gijswobben/customs/Python%20test%20package/master?label=Test%20pipeline&logo=github&logoColor=%23959da5&style=for-the-badge)
[![TestCoverage](https://img.shields.io/codecov/c/github/gijswobben/customs/master?label=Test%20Coverage&logo=Codecov&logoColor=%23959da5&style=for-the-badge)](https://codecov.io/gh/gijswobben/customs)
[![Release](https://img.shields.io/pypi/v/customs?color=%233775A9&label=PyPi%20package%20version&logo=PyPi&logoColor=%23959da5&style=for-the-badge)](https://pypi.org/project/customs/)
[![PythonVersion](https://img.shields.io/pypi/pyversions/customs?color=%233775A9&label=Python%20versions&logo=Python&logoColor=%23959da5&style=for-the-badge)](https://pypi.org/project/customs/)
[![ReadTheDocs](https://img.shields.io/badge/READTHEDOCS-Available-555555?style=for-the-badge&color=brightgreen&logo=Read%20the%20docs&logoColor=%23959da5)](https://customs.readthedocs.io/en/latest/index.html)
# Customs - Authentication made easy
Passport.js inspired library for setting up server authentication in Python.


## Initialize GitHooks
Git hooks can be used to automate certain version control steps, e.g. run tests and style checks before committing. Git hooks for this repository can be found at `./.githooks`, but have to be initialized manually on the development machine with this command:

```
chmod +x .githooks/prepare-commit-msg
git config core.hooksPath .githooks
```
