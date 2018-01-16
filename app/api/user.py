# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from .errors import bad_request, internal_error
from ..models import User
from .. import db


@api.route('/user', methods=['GET'])
@jwt_required
def userget():
    user_id = get_jwt_identity()
    user = User.query.filter_by(id=user_id).first()

    return jsonify(user.to_json()), 200

