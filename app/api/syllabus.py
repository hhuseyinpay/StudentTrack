# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from . import api
from .errors import bad_request, internal_error, forbidden
from ..models import StudentSyllabus
from .. import db
from .utils import is_teacher


@api.route('/syllabus/<int:user_id>', methods=['GET'])
@jwt_required
def syllabusget(user_id):
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

    syllabuses = StudentSyllabus.query.filter_by(student_id=user_id).all()

    return jsonify([syllabus.to_json() for syllabus in syllabuses]), 200


@api.route('/syllabus/<int:user_id>', methods=['POST'])
@jwt_required
def syllabuspost(user_id):
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

    contents = []
    req = request.json.get('done')
    for r in req:
        if not StudentSyllabus.query.filter_by(student_id=r.get("content_id")):
            return bad_request("invalied content_id")
        c = StudentSyllabus.from_json(user_id, r.get("content_id"))
        contents.append(c)
    try:
        db.session.add_all(contents)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")
    return jsonify("OK"), 200


@api.route('/syllabus/<int:student_id>', methods=['PUT'])
@jwt_required
def syllabusput(student_id):
    role_id = get_jwt_claims().get("role_id")
    if role_id == 2:
        if not is_teacher(student_id):
            return forbidden("You have not authorized on class")
    elif role_id == 1:
        pass
    else:
        return internal_error("Authority")

    update = []
    req = request.json.get('update')
    for r in req:
        syllabus = StudentSyllabus.query.filter_by(student_id=student_id).filter_by(
            content_id=r.get("content_id")).first()
        if syllabus is None:
            return bad_request("invalied content_id")

        syllabus.status = r.get('status')
        update.append(syllabus)

    try:
        db.session.add_all(update)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")

    return jsonify("OK"), 200
