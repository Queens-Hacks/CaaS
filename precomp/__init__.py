# -*- coding: utf-8 -*-
"""
    precomp
    ~~~~~~~

    la la la

    :copyright: 2014 Carey Metcalfe, Graham McGregor, Phil Schleihauf
"""

from os import environ
from werkzeug.exceptions import NotFound
from flask import Flask, url_for, redirect, render_template

class SubFlask(Flask):
    def route(self, rule, *args, **kwargs):
        if self.debug:
            subdomain = kwargs.pop('subdomain', None)
            if subdomain is not None:
                rule = '/subdomain/{}/{}'.format(subdomain, rule)
        return super(SubFlask, self).route(rule, *args, **kwargs)

app = SubFlask(__name__)
app.config.update(
    DEBUG=environ.get('DEBUG') == 'True',
    SECRET_KEY=environ['SECRET_KEY'],
    GITHUB_CLIENT_ID=environ['GITHUB_CLIENT_ID'],
    GITHUB_CLIENT_SECRET=environ['GITHUB_CLIENT_SECRET'],
)


# we can import other stuff now that we have a reference to app.
from . import account


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/", subdomain="<sub>")
def get_service(sub):
    """routes subdomains to the right service"""
    return "hello"
