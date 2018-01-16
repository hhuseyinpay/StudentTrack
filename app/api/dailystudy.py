# -*- coding: utf-8 -*-
from flask import request, jsonify, json
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime, timedelta
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import extract
from . import api
from .errors import bad_request, internal_error
from ..models import DailyStudy, DailyStudyCourse, Role
from .. import db


@api.after_app_request
def after_request(response):
    for query in get_debug_queries():
        print(
            'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
            % (query.statement, query.parameters, query.duration,
               query.context))
    return response


@api.route('/dailystudy/getday/<string:day>', methods=['GET'])
@jwt_required
def dgetbydat(day):
    user_id = get_jwt_identity()
    try:
        date = day.split("-")
        studies = DailyStudy.query.filter_by(student_id=user_id).filter(
            extract('day', DailyStudy.date) == date[0], extract('month', DailyStudy.date) == date[1],
            extract('year', DailyStudy.date) == date[2]).all()

        print(studies)
    except Exception:
        print(Exception)
        return bad_request("incorrect day parameter")
    return jsonify([study.to_json() for study in studies]), 200


@api.route('/dailystudy/getinterval/<string:startdate>/<string:enddate>', methods=['GET'])
@jwt_required
def dgetbyinterval(startdate, enddate):
    user_id = get_jwt_identity()
    try:
        startdate = datetime.strptime(startdate, "%d-%m-%Y")
        enddate = datetime.strptime(enddate, "%d-%m-%Y")

        studies = DailyStudy.query.filter_by(student_id=user_id).filter(DailyStudy.date > startdate,
                                                                        DailyStudy.date < enddate).all()
    except Exception:
        print(Exception)
        return bad_request("incorrect day parameter")
    return jsonify([study.to_json() for study in studies]), 200


@api.route('/dailystudy', methods=['POST'])
@jwt_required
def dailystudypost():
    user_id = get_jwt_identity()
    role = get_jwt_claims().get("role")
    role_id = Role.query.filter_by(name=role).first().id

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
    except Exception:
        print(Exception)
        return internal_error("db problem")
    return jsonify("OK"), 200


@api.route('/dailystudy', methods=['GET'])
@jwt_required
def dailystudyget():
    role = get_jwt_claims().get("role")
    role_id = Role.query.filter_by(name=role).first().id

    courses = DailyStudyCourse.query.filter_by(role_id=role_id).all()

    return jsonify([course.course.name for course in courses]), 200
