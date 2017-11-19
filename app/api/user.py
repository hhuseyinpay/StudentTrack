from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta

from . import api
from ..models import DailyStudy


@jwt_required
@api.route('/dailystudy/<int:day>', methods=['GET'])
def dailystudy(day):
    user_id = get_jwt_identity()
    time = datetime.utcnow() - timedelta(days=day)

    studies = DailyStudy.query.filter_by(student_id=user_id).filter(DailyStudy.date > time).all()

    return jsonify([study.to_json() for study in studies]), 200
