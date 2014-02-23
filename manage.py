#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage
    ~~~~~~

    Management utilities for caas
"""

from flask.ext.script import Manager
from precomp import app
import atexit


manager = Manager(app)


@manager.command
def hello():
    """This command says hello"""
    print('hello')

@manager.command
def runclient(config="client/config.yaml"):
    """Runs the client for a type of processor on a given directory"""

    from client.client import Client

    c = Client(config)
    c.start_watching()

    @atexit.register
    def on_exit():
        if c:
            c.stop_watching()

if __name__ == '__main__':
    manager.run()
