# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from . import api
from .errors import internal_error, forbidden, bad_request
from .utils import is_teacher
from ..models import User
from .. import db


@api.route('/user/<int:user_id>', methods=['GET'])
@jwt_required
def userget(user_id):
    role_id = get_jwt_claims().get("role_id")

    if user_id == 0:
        user_id = get_jwt_identity()
    elif role_id == 1:
        pass
    elif role_id == 2:
        if not is_teacher(user_id):
            return forbidden("You have not authorized on class")
    else:
        return internal_error("Authority")

    user = User.query.filter_by(id=user_id).first()

    return jsonify(user.to_json()), 200


@api.route('/user', methods=['POST'])
@jwt_required
def userpost():
    role_id = get_jwt_claims().get("role_id")

    if role_id == 1 or role_id == 2:
        pass
    else:
        return internal_error("Authority")

    user = User.from_json(request.json)
    if user is None:
        return bad_request("incorrect user detail")
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")
    return jsonify("OK"), 200


@api.route('/user/<int:user_id>', methods=['PUT'])
@jwt_required
def userput(user_id):
    role_id = get_jwt_claims().get("role_id")

    if user_id == 0:
        user_id = get_jwt_identity()
    elif role_id == 1:
        pass
    elif role_id == 2:
        if not is_teacher(user_id):
            return forbidden("You have not authorized on class")
    else:
        return internal_error("Authority")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return bad_request("wrong user_id")
    req = request.json
    try:
        username = req.get("username")
        if username is not None:
            if User.query.filter_by(username=username).first() is None:
                user.username = username
            else:
                return bad_request("Username is already exist")

        name = req.get("name")
        if name is not None:
            user.name = name

        password = req.get("password")
        if password is not None:
            user.hash_password(password)

        if role_id == 2:
            role = req.get("role_id")
            if role is not None and role > role_id:
                user.role_id = role

        if role_id == 1:
            role = req.get("role_id")
            if role is not None:
                user.role_id = role

            class_id = req.get("class_id")
            if class_id is not None:
                user.class_id = class_id

        db.session.add(user)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")
    return jsonify("OK"), 200


@api.route('/userlist', methods=['GET'])
@jwt_required
def userlist():
    role_id = get_jwt_claims().get("role_id")

    if role_id == 1:
        users = User.query.all()
    elif role_id == 2:
        uid = get_jwt_identity()
        cid = User.query.filter_by(id=uid).first().class_id
        users = User.query.filter_by(class_id=cid).all()
    else:
        return internal_error("Authority")

    return jsonify([user.to_json() for user in users]), 200
