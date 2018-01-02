from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt_claims
from datetime import datetime, timedelta
from flask_sqlalchemy import get_debug_queries
from sqlalchemy import extract
from . import api
from .errors import bad_request
from ..models import DailyStudy


@api.after_app_request
def after_request(response):
    for query in get_debug_queries():
        print(
            'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
            % (query.statement, query.parameters, query.duration,
               query.context))
    return response


@api.route('/dailystudy/getbyday/<string:day>', methods=['GET'])
@jwt_required
def dgetbydat(day):
    user_id = get_jwt_identity()
    date = day.split("-")
    try:
        studies = DailyStudy.query.filter_by(student_id=user_id).filter(
            extract('day', DailyStudy.date) == date[0], extract('month', DailyStudy.date) == date[1],
            extract('year', DailyStudy.date) == date[2]).all()

        print(studies)
    except Exception as e:
        print(e)
        return bad_request("incorrect day parameter")
    return jsonify([study.to_json() for study in studies]), 200


@api.route('/dailystudy/getbyinterval/<string:startday>/<string:endday>', methods=['POST'])
@jwt_required
def dgetbyinterval(startday, endday):
    user_id = get_jwt_identity()
    req = request.json.get('request')
    if req == "getbyinterval":
        try:
            startday = request.json.get('startday')
            endday = request.json.get('endday')
            studies = DailyStudy.query.filter_by(student_id=user_id).filter(DailyStudy.date > startday).filter(
                DailyStudy.date < endday).all()
        except:
            return bad_request("incorrect day parameter")
        return jsonify([study.to_json() for study in studies]), 200

    return bad_request("body")


@api.route('/dailystudy/settoday', methods=['POST'])
@jwt_required
def dsettoday():
    user_id = get_jwt_identity()
    req = request.json.get('request')

    # time = datetime.utcnow() - timedelta(days=int(day))
    if req == "settoday":
        today = request.json.get('today')

        print(today)
        return "0"

    return bad_request("body")


@api.route('/dailystudy', methods=['GET'])
@jwt_required
def dailystudyget():
    return "0"
