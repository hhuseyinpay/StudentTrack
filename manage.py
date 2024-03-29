#!/usr/bin/env python
import os

from flask_script import Manager

from app import create_app, db

app = create_app('development')

manager = Manager(app)


@manager.command
def createdb():
    """Creates the db tables."""
    db.create_all()


@manager.command
def dropdb():
    """Drops the db tables."""
    db.drop_all()


@manager.command
def cr():
    db.drop_all()
    db.create_all()


@manager.command
def fakedata():
    from app.models import User, DailyStudy

    u1 = User(0, 'admin', "admin")
    u = [u1]
    c1 = DailyStudy(amount=5, student_id=1, course_id=3)
    c = [c1]
    #for i in range(1,500000):
    #    c.append(DailyStudy(amount=3, student_id=3, course_id=3))
    #db.session.add_all(u)
    db.session.add_all(c)
    db.session.commit()


if __name__ == '__main__':
    manager.run()
