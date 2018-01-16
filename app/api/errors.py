from flask import jsonify

from . import api


def internal_error(message):
    response = jsonify({'error': 'internal', 'msg': message})
    response.status_code = 500
    return response


def bad_request(message):
    response = jsonify({'error': 'bad request', 'msg': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'msg': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'msg': message})
    response.status_code = 403
    return response


class ValidationError(ValueError):
    pass


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
