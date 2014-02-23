# -*- coding: utf-8 -*-
import tempfile
from os import environ
from shutil import rmtree
from utils import tar_paths, untar_to_path
from werkzeug.exceptions import NotFound
from flask import Flask, url_for, redirect, render_template, request, Response

class SubFlask(Flask):
    def route(self, rule, *args, **kwargs):
        if self.debug:
            subdomain = kwargs.pop('subdomain', None)
            if subdomain is not None:
                rule = '/subdomain/{}/{}'.format(subdomain, rule)
        return super(SubFlask, self).route(rule, *args, **kwargs)

app = SubFlask(__name__)
try:
    app.config.update(
        DEBUG=environ.get('DEBUG') == 'True',
        SECRET_KEY=environ['SECRET_KEY'],
        MONGO_URI=environ['MONGO_URI'],
        GITHUB_CLIENT_ID=environ['GITHUB_CLIENT_ID'],
        GITHUB_CLIENT_SECRET=environ['GITHUB_CLIENT_SECRET'],
    )
except KeyError as e:
    from .config import CONFIG
    app.config.update(CONFIG)


# we can import other stuff now that we have a reference to app.
from . import account


@app.route("/")
def home():
    return render_template("home.html")



def unpack_file(zfile):
    """Unpacks files and returns the path"""

    temp_dir = tempfile.mkdtemp()

    untar_to_path(zfile, temp_dir)

    return temp_dir


def pack_and_clean(directory):
    """Compresses the files in the directory and then deletes the directory"""

    stream = tar_paths(directory)

    rmtree(directory)

    return stream


processors = {}

def processor(lang):
    def decorate(func):
        processors[lang] = func
        return func
    return decorate

@processor('sass')
def sass_proc(input_dir):

    # output_dir = tempfile.mkdtemp()
    # process stuff

    return input_dir


@app.route("/<processor>", methods=['POST'])
def get_service(processor):
    """routes subdomains to the right service"""
    if processor not in processors:
        return Response ("invalid processor {}".format(processor), status=400)

    elif request.files is None:
        return Response ("no files recieved, should be 1", status=400)

    elif len(request.files) != 1:
        return Response ("should send 1 file, sent {}".format(len(request.files)), status=400)

    elif request.files['data'] is None:
        return Response ("form key should be 'data'", status=400)

    temp_dir = unpack_file(request.files['data'])

    output_dir = (processors[processor])(temp_dir)

    data = pack_and_clean(temp_dir)

    return Response(data, mimetype="application/gzip")
