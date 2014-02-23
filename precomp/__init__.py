# -*- coding: utf-8 -*-
import tempfile
import os
import subprocess
from utils import tar_paths, untar_to_path, rmrf
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


processors = {}


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
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.communicate()
        return (p.returncode, ret)
    except EnvironmentError as e:
        return (255, (None, "Server error: {0} - {1}".format(type(e).__name__, e).encode("utf-8")))


def processor(lang):
    def decorate(func):
        processors[lang] = func
        return func
    return decorate


# we can import other stuff now that we have a reference to app and everything.
from . import account
from . import processors


@app.route("/<processor>", methods=['POST'])
def get_service(processor):
    """routes subdomains to the right service"""

    if processor not in processors:
        return Response ("Invalid processor '{0}'. Valid processors are: {1}".format(processor, ", ".join(processors)), status=400)

    elif request.files is None:
        return Response ("No files recieved, should be 1", status=400)

    elif len(request.files) != 1:
        return Response ("Should send 1 file, sent {0} instead".format(len(request.files)), status=400)

    elif request.files['data'] is None:
        return Response ("Form key should be 'data'", status=400)

    in_dir = tempfile.mkdtemp()
    out_dir = tempfile.mkdtemp()

    code = 255

    try:
        untar_to_path(request.files['data'], in_dir)

        # Compile the code
        code = (processors[processor])(in_dir, out_dir)

        stream = tar_paths(out_dir)
    finally:
        rmrf(in_dir)
        rmrf(out_dir)

    r = Response(stream, mimetype="application/gzip")
    if code != 0:
        r.headers.add('warning', "Compilation returned non-zero exit code {0}".format(code))

    return r
