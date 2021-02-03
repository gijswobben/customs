# Development

## Initialize GitHooks
Git hooks can be used to automate certain version control steps, e.g. run tests and style checks before committing. Git hooks for this repository can be found at `./.githooks`, but have to be initialized manually on the development machine with this command:

```
chmod +x .githooks/prepare-commit-msg
git config core.hooksPath .githooks
```
