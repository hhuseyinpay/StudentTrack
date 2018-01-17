# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy, get_debug_queries
from config import config

db = SQLAlchemy()


def sql_debug(response):
    queries = list(get_debug_queries())
    query_str = ''
    total_duration = 0.0
    for q in queries:
        total_duration += q.duration
        stmt = str(q.statement % q.parameters).replace('\n', '\n       ')
        query_str += 'Query: {0}\nDuration: {1}ms\n\n'.format(stmt, round(q.duration * 1000, 2))

    print('=' * 80)
    print(' SQL Queries - {0} Queries Executed in {1}ms'.format(len(queries), round(total_duration * 1000, 2)))
    print('=' * 80)
    print(query_str.rstrip('\n'))
    print('=' * 80 + '\n')

    return response


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # app.config['JSON_AS_ASCII'] = False
    app.config['MAX_CONTENT_LENGTH'] = 1000
    db.init_app(app)

    if config_name == 'debug':
        app.after_request(sql_debug)

    @app.route
    def get():
        return

    jwt = JWTManager(app)

    @jwt.expired_token_loader
    def my_expired_token_callback():
        return jsonify({
            'status': 401,
            'msg': 'The token has expired'
        }), 401

    @jwt.user_claims_loader
    def add_claims_to_access_token(identity):
        from .models import User
        user = User.query.filter_by(id=identity).first()
        return {
            'user_id': identity,
            'role_id': user.role.id
        }

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
