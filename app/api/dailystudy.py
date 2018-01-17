# -*- coding: utf-8 -*-
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime
from sqlalchemy import extract
from . import api
from .errors import bad_request, internal_error, forbidden
from ..models import DailyStudy, DailyStudyCourse
from .. import db
from .utils import is_teacher


@api.route('/dailystudy/getday/<int:user_id>/<string:day>', methods=['GET'])
@jwt_required
def dgetbydate(user_id, day):
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

    try:
        date = day.split("-")
        studies = DailyStudy.query.filter_by(student_id=user_id).filter(
            extract('day', DailyStudy.date) == date[0], extract('month', DailyStudy.date) == date[1],
            extract('year', DailyStudy.date) == date[2]).all()

    except Exception as e:
        print(e)
        return bad_request("incorrect day parameter")
    return jsonify([study.to_json() for study in studies]), 200


@api.route('/dailystudy/getinterval/<int:user_id>/<string:startdate>/<string:enddate>', methods=['GET'])
@jwt_required
def dgetbyinterval(startdate, enddate, user_id):
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

    try:
        startdate = datetime.strptime(startdate, "%d-%m-%Y")
        enddate = datetime.strptime(enddate, "%d-%m-%Y")

        studies = DailyStudy.query.filter_by(student_id=user_id).filter(DailyStudy.date > startdate,
                                                                        DailyStudy.date < enddate).all()
    except Exception as e:
        print(e)
        return bad_request("incorrect day parameter")
    return jsonify([study.to_json() for study in studies]), 200


@api.route('/dailystudy/<int:user_id>', methods=['POST'])
@jwt_required
def dailystudypost(user_id):
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

    courses = DailyStudyCourse.query.filter_by(role_id=role_id).all()
    course_ids = [course.course_id for course in courses]

    course = []
    req = request.json.get('done')
    for r in req:
        if not r.get("course_id") in course_ids:
            return bad_request("invalied course_id")
        c = DailyStudy.from_json(user_id, r)
        course.append(c)

    try:
        db.session.add_all(course)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")

    return jsonify("OK"), 200


@api.route('/dailystudy/<int:student_id>', methods=['PUT'])
@jwt_required
def dailystudyput(student_id):
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
        study = DailyStudy.query.filter_by(id=r.get("dailystudy_id")).filter_by(student_id=student_id).first()
        if study is None:
            return bad_request("invalied dailystudy_id")

        study.status = r.get('status')
        study.amount = r.get('amount')
        update.append(study)

    try:
        db.session.add_all(update)
        db.session.commit()
    except Exception as e:
        print(e)
        return internal_error("db problem")

    return jsonify("OK"), 200


@api.route('/dailystudy', methods=['GET'])
@jwt_required
def dailystudyget():
    role_id = get_jwt_claims().get("role_id")

    courses = DailyStudyCourse.query.filter_by(role_id=role_id).filter_by(status=True).all()

    return jsonify([course.to_json() for course in courses]), 200
