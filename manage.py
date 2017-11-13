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


if __name__ == '__main__':
    manager.run()