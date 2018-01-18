# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_claims
from . import api
from .errors import internal_error
from ..models import Class
from .. import db


@api.route('/class', methods=['GET'])
@jwt_required
def classget():
    role_id = get_jwt_claims().get("role_id")

    if role_id == 1:
        return internal_error("Authority")

    classes = Class.query.all()

    return jsonify([clas.to_json() for clas in classes]), 200

