from typing import Optional


class HTTPException(Exception):

    _default_message: str = ""
    _default_status_code: int = 400

    def __init__(
        self,
        message: Optional[str] = None,
        status_code: Optional[int] = None,
    ) -> None:

        # Store the error message
        if message is None:
            message = self._default_message
        self.message = message

        # Store the response status code
        if status_code is None:
            self.status_code = self._default_status_code
        else:
            self.status_code = status_code
        super().__init__(message)


class UnauthorizedException(HTTPException):
    _default_message: str = "Unauthorized"
    _default_status_code: int = 401
