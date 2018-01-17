from . import api
from ..models import User
from flask_sqlalchemy import get_debug_queries
from flask_jwt_extended import get_jwt_identity


@api.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration > 0.002:
            print(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response


def is_teacher(student_id):
    uid = get_jwt_identity()
    cid = User.query.filter_by(id=uid).first()
    sid = User.query.filter_by(id=student_id).first()
    if cid is None or sid is None:
        return False
    return sid.class_id == cid.class_id
