from flask import request, jsonify
from flask_jwt_extended import jwt_required, create_access_token, get_jwt_claims

from .errors import bad_request
from ..models import *

from . import api


@api.route('/login', methods=['POST'])
def login():
    """
    :Method: POST
    :Request Header: Content-Type:application/json
    :Body:          { 'username':'username', 'password':'password'}
     
    :return:        { "access_token": " ... " }
    """

    if not request.is_json:
        return bad_request("Missing JSON in request")

    username = request.json.get('username')
    password = request.json.get('password')

    if not username:
        return bad_request("Missing username parameter")
    if not password:
        return bad_request("Missing password parameter")

    user = User.query.filter_by(username=username).first()

    if user is None or not user.verify_password(password=password):
        return bad_request("Bad username or password")
    user.ping()
    ret = {'access_token': create_access_token(identity=user.id)}
    return jsonify(ret), 200


# This api should be used for debug
@api.route('/get')
@jwt_required
def get():
    return jsonify(get_jwt_claims()), 200
