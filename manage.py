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


if __name__ == '__main__':
    manager.run()
