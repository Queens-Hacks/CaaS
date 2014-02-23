# -*- coding: utf-8 -*-
import tempfile
import os
import shutil
import subprocess
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
        DEBUG=os.environ.get('DEBUG') == 'True',
        SECRET_KEY=os.environ['SECRET_KEY'],
        MONGO_URI=os.environ['MONGO_URI'],
        GITHUB_CLIENT_ID=os.environ['GITHUB_CLIENT_ID'],
        GITHUB_CLIENT_SECRET=os.environ['GITHUB_CLIENT_SECRET'],
    )
except KeyError as e:
    try:
        from .config import CONFIG
    except ImportError:
        raise e
    app.config.update(CONFIG)


# we can import other stuff now that we have a reference to app.
from . import account

@app.route("/")
def home():
    return render_template("home.html")


def rmrf(path):
    """Just delete it, dude"""

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)

def output_logs(out_dir, code, output):
    log_dir = os.path.join(out_dir, "__precomp__")
    os.mkdir(log_dir)

    names = ("out", "err")
    for i in range(2):
        if output[i]:
            with open(os.path.join(log_dir, "std{0}.txt".format(names[i])), 'w') as f:
                f.write(output[i].decode("utf-8"))

    # Ugly hack - find a better way
    open(os.path.join(log_dir, "EXIT STATUS - {0}".format(code)), 'a').close()


def system_call(args):
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    ret = p.communicate()
    return (p.returncode, ret)


processors = {}

def processor(lang):
    def decorate(func):
        processors[lang] = func
        return func
    return decorate


@processor('sass')
def sass_proc(in_dir, out_dir):
    """compiles main.sass in the input directory"""
    MAIN_SASS = "main.sass"
    OUTPUT_FILE = "main.css"

    code, output = system_call(("sass", os.path.join(in_dir, MAIN_SASS), os.path.join(out_dir, OUTPUT_FILE)))

    output_logs(out_dir, code, output)

@processor('scss')
def scss_proc(in_dir, out_dir):
    """compiles main.sass in the input directory"""
    MAIN_SCSS = "main.scss"
    OUTPUT_FILE = "main.css"

    code, output = system_call(("sass", os.path.join(in_dir, MAIN_SASS), os.path.join(out_dir, OUTPUT_FILE)))

    output_logs(out_dir, code, output)

@app.route("/<processor>", methods=['POST'])
def get_service(processor):
    """routes subdomains to the right service"""

    if processor not in processors:
        return Response ("Invalid processor {0}".format(processor), status=400)

    elif request.files is None:
        return Response ("No files recieved, should be 1", status=400)

    elif len(request.files) != 1:
        return Response ("Should send 1 file, sent {0} instead".format(len(request.files)), status=400)

    elif request.files['data'] is None:
        return Response ("Form key should be 'data'", status=400)

    in_dir = tempfile.mkdtemp()
    out_dir = tempfile.mkdtemp()

    try:
        untar_to_path(request.files['data'], in_dir)

        # Compile the code
        (processors[processor])(in_dir, out_dir)

        stream = tar_paths(out_dir)
    finally:
        rmrf(in_dir)
        rmrf(out_dir)

    return Response(stream, mimetype="application/gzip")
