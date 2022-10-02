from flask import current_app
from pydantic import ValidationError

class APIException(Exception):
    """
    Base API Exception
    """

    def __init__(
        self,
        message: str,
        status_code: int = 500,
        payload: dict = None,
        name: str = None
    ):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload
        self.name = name

    def to_dict(self):
        """
        To dict
        """
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status_code'] = self.status_code
        rv['name'] = self.name
        return rv

class InvalidPayloadException(APIException):
    """
    400 Invalid Payload Exception
    """

    def __init__(
        self,
        message: str = 'Invalid payload',
        payload: dict = None,
        name: str = 'InvalidPayloadException'
    ):
        super().__init__(
            message=message,
            status_code=400,
            payload=payload,
            name=name
        )

class ValidationException(InvalidPayloadException):
    """
    400 Validation Exception
    """

    def __init__(
        self,
        err: ValidationError,
        message: str = 'Validation error'
    ):
        payload = dict({
            'errors': [
                {
                    'field': error['loc'][0],
                    'message': error['msg']
                } for error in err.errors()
            ]
        })
        super().__init__(
            message=message,
            payload=payload,
        )

class BadRequestException(APIException):
    """
    400 Bad Request Exception
    """

    def __init__(
        self,
        message: str = 'Bad Request',
        payload: dict = None,
        name: str ='Bad Request'
    ):
        super().__init__(
            message=message,
            status_code=400,
            payload=payload,
            name=name
        )


class UnauthorizedException(APIException):
    """
    401 Unauthorized Exception
    """

    def __init__(
        self,
        message: str = 'Not Authorized to perform this action',
        payload: dict = None,
        name: str = 'Unauthorized'
    ):
        super().__init__(
            message=message,
            status_code=401,
            payload=payload,
            name=name
        )


class ForbiddenException(APIException):
    """
    403 Forbidden Exception
    """

    def __init__(
        self,
        message: str = 'Forbidden',
        payload: dict = None,
        name: str = 'Forbidden'
    ):
        super().__init__(
            message=message,
            status_code=403,
            payload=payload,
            name=name
        )


class NotFoundException(APIException):
    """
    404 Not Found Exception
    """

    def __init__(
        self,
        message: str = 'The requested URL was not found on the server.',
        payload: dict = None,
        name: str = 'Not Found'
    ):
        super().__init__(
            message=message,
            status_code=404,
            payload=payload,
            name=name
        )


class ServerErrorException(APIException):
    """
    500 Internal Server Error Exception
    """

    def __init__(
        self,
        message: str = 'Something went wrong',
        payload: dict = None,
        name: str = 'Internal Server Error'
    ):
        super().__init__(
            message=message,
            status_code=500,
            payload=payload,
            name=name
        )


class NotImplementedException(APIException):
    """
    501 Not Implemented Exception
    """

    def __init__(
        self,
        message: str = 'The method is not implemented for the requested URL.',
        payload: dict = None,
        name: str = 'Not Implemented'
    ):
        super().__init__(
            message=message,
            status_code=501,
            payload=payload,
            name=name
        )


class MethodNotAllowedException(APIException):
    """
    405 Method Not Allowed
    """

    def __init__(
        self,
        message: str = 'The method is not allowed for the requested URL.',
        payload: dict = None,
        name: str = 'Method Not Allowed'
    ):
        super().__init__(
            message=message,
            status_code=405,
            payload=payload,
            name=name
        )