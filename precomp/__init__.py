# -*- coding: utf-8 -*-
"""
    precomp
    ~~~~~~~

    la la la

    :copyright: 2014 Carey Metcalfe, Graham McGregor, Phil Schleihauf
"""

from werkzeug.exceptions import NotFound

from flask import Flask, url_for, redirect

class SubFlask(Flask):
    def route(self, rule, *args, **kwargs):
        if self.debug:
            subdomain = kwargs.pop('subdomain', None)
            if subdomain is not None:
                rule = '/subdomain/{}/{}'.format(subdomain, rule)
        return super(SubFlask, self).route(rule, *args, **kwargs)

app = SubFlask(__name__)
app.config.update(dict(
    DEBUG=True
))

@app.route("/")
def home():
    return "home page"

@app.route("/", subdomain="<sub>")
def get_service(sub):
    """routes subdomains to the right service"""
    return "hello"
