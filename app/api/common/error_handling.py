from flask import jsonify, json, current_app
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden, MethodNotAllowed, NotImplemented, BadRequest, InternalServerError, HTTPException
from ...api.common.utils.exceptions import APIException, ServerErrorException, NotFoundException, UnauthorizedException, \
    ForbiddenException, MethodNotAllowedException, NotImplementedException, BadRequestException

def handle_exception(err: APIException):
    """
    Handle Exception
    """
    response = jsonify(err.to_dict())
    response.content_type = "application/json"
    response.status_code = err.status_code
    return response

def handle_generic_exception(err: Exception):
    """
    Handle Generic Exception
    """
    return handle_exception(ServerErrorException())

def handle_werkzeug_exception(err: HTTPException):
    """
    Handle Werkzeug Exception
    """
    if isinstance(err, NotFound):
        return handle_exception(NotFoundException(message=err.description))
    elif isinstance(err, Unauthorized):
        return handle_exception(UnauthorizedException(message=err.description))
    elif isinstance(err, Forbidden):
        return handle_exception(ForbiddenException(message=err.description))
    elif isinstance(err, MethodNotAllowed):
        return handle_exception(MethodNotAllowedException(message=err.description))
    elif isinstance(err, NotImplemented):
        return handle_exception(NotImplementedException(message=err.description))
    elif isinstance(err, BadRequest):
        return handle_exception(BadRequestException(message=err.description))
    else:
        return handle_exception(ServerErrorException(message=err.description))
