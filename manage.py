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
def runclient(service, directory="."):
    """Runs the client for a type of processor on a given directory"""
    from client.client import Client
    print ("service arg: " + service)
    if service is not None:
        c = Client(service, directory)
        c.start_watching()

    @atexit.register
    def on_exit():
        print ("in after thing")
        if c:
            c.stop_watching()

if __name__ == '__main__':
    manager.run()
