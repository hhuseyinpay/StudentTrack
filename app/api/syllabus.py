# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from . import api
from .errors import bad_request, internal_error
from ..models import StudentSyllabus
from .. import db


@api.route('/syllabus', methods=['GET'])
@jwt_required
def syllabusget():
    user_id = get_jwt_identity()
    syllabuses = StudentSyllabus.query.filter_by(student_id=user_id).all()

    return jsonify([syllabus.to_json() for syllabus in syllabuses]), 200


@api.route('/syllabus', methods=['POST'])
@jwt_required
def syllabuspost():
    user_id = get_jwt_identity()

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
