from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash
# from itsdangerous import (TimedJSONWebSignatureSerializer
# as Serializer)
# from flask import current_app
from . import db
from .api.errors import ValidationError


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod  # default roles ?
    def insert_roles():
        role1 = Role(name='student')
        role2 = Role(name='teacher')
        role3 = Role(name='admin')

        db.session.add(role1)
        db.session.add(role2)
        db.session.add(role3)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    username = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)

    name = db.Column(db.String)

    enroll_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)


syllabus = db.Table('syllabus', db.metadata,
                    db.Column('content_id', db.Integer, db.ForeignKey('contents.id'), primary_key=True),
                    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True))


class Content(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    amount = db.Column(db.Float)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    contents = db.relationship('Content',
                               secondary=syllabus, backref='courses')


class StudentSyllabus(db.Model):
    __tablename__ = 'student_syllabuses'

    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)

    date = db.Column(db.DateTime(), default=datetime.utcnow)
