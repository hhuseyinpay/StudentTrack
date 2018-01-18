from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer)
from flask import current_app
from . import db


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)

    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod  # default roles ?
    def insert_roles():
        role1 = Role(name='Manager')
        role2 = Role(name='Teacher')
        role3 = Role(name='Student')

        db.session.add(role1)
        db.session.add(role2)
        db.session.add(role3)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, index=True, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True)

    username = db.Column(db.String, index=True, unique=True)
    password_hash = db.Column(db.String)
    name = db.Column(db.String)

    enroll_date = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # duyuruya ping koy!

    # daily_study = db.relationship('daily_studies', backref='student')

    @staticmethod
    def from_json(json_user):
        username = json_user.get('username')
        password = json_user.get('password')
        name = json_user.get('name')
        role_id = json_user.get('role_id')
        class_id = json_user.get('class_id')

        if username is None or password is None or name is None or role_id is None or class_id is None:
            return None
        return User(role_id, name, username, password, class_id)

    def to_json(self):
        if self.class_id is None or self.class_id == 0:
            return {
                "user_id": self.id,
                "role_name": self.role.name,
                "role_id": self.role_id,
                "class_name": "",
                "class_id": 0,
                "username": self.username,
                "name": self.name,
                "enroll_date": self.enroll_date,
                "last_seen": self.last_seen
            }
        else:
            return {
                "user_id": self.id,
                "role_name": self.role.name,
                "role_id": self.role_id,
                "class_name": self.classs.name,
                "class_id": self.class_id,
                "username": self.username,
                "name": self.name,
                "enroll_date": self.enroll_date,
                "last_seen": self.last_seen
            }

    def __init__(self, role_id, name, username, password, class_id=None):
        self.role_id = role_id
        self.class_id = class_id
        self.name = name
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
            print("verify auth data: {}".format(data))
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

    def to_json(self):
        return {
            "student_id": self.student_id,
            "content_id": self.content_id,
            "course_name": self.content.course.name,
            "content_name": self.content.name,
            "content_description": self.content.description,
            "content_amount": self.content.amount,
            "date": self.date,
            "status": self.status
        }

    @staticmethod
    def from_json(student_id, content_id):
        return StudentSyllabus(student_id=student_id, content_id=content_id)


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
    def from_json(sid, json_study):
        cid = json_study.get('course_id')
        amount = json_study.get('amount')
        return DailyStudy(student_id=sid, course_id=cid, amount=amount)

    def to_json(self):
        return {
            "dailystudy_id": self.id,
            "course_id": self.course_id,
            "course_name": str(self.course.name),
            "amount": self.amount,
            "date": self.date,
            "status": self.status
        }


class DailyStudyCourse(db.Model):
    __tablename__ = 'daily_study_courses'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    course = db.relationship('Course')

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    role = db.relationship('Role')

    status = db.Column(db.Boolean, default=False)

    def to_json(self):
        return {
            "course_name": self.course.name,
            "course_id": self.course.id
        }


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    name = db.Column(db.String)
    description = db.Column(db.String)

    students = db.relationship('User', foreign_keys=[User.class_id], backref='classs')

    def to_json(self):
        return {
            "class_id": self.id,
            "manager_id": self.manager_id,
            "name": self.name,
            "description": self.description
        }
