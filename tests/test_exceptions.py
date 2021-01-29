from customs.exceptions import UnauthorizedException, HTTPException


def test_UnauthorizedException():

    # Create a instances of the exception to test
    exceptions = [UnauthorizedException(), UnauthorizedException("Test", 404)]

    # Test all instances
    for exception in exceptions:

        # Make sure it has the right subclass
        assert isinstance(
            exception, HTTPException
        ), "All exceptions should subclass the HTTPException"

        # Make sure it has a message and status code
        assert (
            hasattr(exception, "message")
            and isinstance(exception.message, str)
            and exception.message != ""
        ), "UnauthorizedException has no valid 'message' attribute"

        assert (
            hasattr(exception, "status_code")
            and isinstance(exception.status_code, int)
            and exception.status_code >= 100
            and exception.status_code <= 900
        ), "UnauthorizedException doesn't have a valid status code"
