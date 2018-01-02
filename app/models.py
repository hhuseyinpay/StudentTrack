from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer)
from flask import current_app
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
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)

    username = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)
    name = db.Column(db.String)

    enroll_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)

    # daily_study = db.relationship('daily_studies', backref='student')

    def __init__(self, role_id, username, password, class_id=None):
        self.role_id = role_id
        self.class_id = class_id
        self.username = username
        self.password_hash = generate_password_hash(password)

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print("verify auth data: {}".fortmat(data))
        except:
            return None  # invalid token
        return User.query.get(data['id'])

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)


class Content(db.Model):
    __tablename__ = 'contents'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    description = db.Column(db.String)
    amount = db.Column(db.Float)

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    students = db.relationship('StudentSyllabus', backref='content')

    def __init__(self, name, description, amount, course_id):
        self.name = name
        self.description = description
        self.amount = amount
        self.course_id = course_id


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    contents = db.relationship('Content', backref='course')

    # daily_study = db.relationship('daily_studies', backref='course')


class StudentSyllabus(db.Model):
    __tablename__ = 'student_syllabuses'

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    content_id = db.Column(db.Integer, db.ForeignKey('contents.id'), primary_key=True)

    date = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean)


class DailyStudy(db.Model):
    __tablename__ = 'daily_studies'

    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    date = db.Column(db.DateTime(), default=datetime.utcnow)
    status = db.Column(db.Boolean, default=False)

    student_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    student = db.relationship('User')

    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    course = db.relationship('Course')

    @staticmethod
    def from_json():
        pass

    def to_json(self):
        print(str(self.course.name))
        return {
            "course_name": str(self.course.name),
            "amount": self.amount,
            "date": self.date,
            "status": self.status
        }


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.String)
    description = db.Column(db.String)

    students = db.relationship('User', foreign_keys=[User.class_id], backref='class')
