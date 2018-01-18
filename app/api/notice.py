# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from ..models import User


@api.route('/notice', methods=['GET'])
@jwt_required
def noticeget():
    uid = get_jwt_identity()
    user = User.query.filter_by(id=uid).first()
    user.ping()  # login olmuştur.

    notices = "test notice"  # Notice.query.filter_by(status=True).all()

    return jsonify(notices), 200  # return jsonify([notice.to_json() for notice in notices]), 200
