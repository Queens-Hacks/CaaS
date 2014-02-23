#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~

    Management utilities for caas
"""

from flask.ext.script import Manager
from precomp import app

manager = Manager(app)


@manager.command
def rewelcome(username):
    from precomp import account
    user = account.User.collection.find_one({'username': username})
    if user is None:
        raise SystemExit('User {} not found.'.format(username))
    del user.dismissed_welcome
    user.save()


@manager.command
def remove(username):
    from precomp import account
    user = account.User.collection.find_one({'username': username})
    if user is None:
        raise SystemExit('User {} not found.'.format(username))
    user.remove()


if __name__ == '__main__':
    manager.run()
