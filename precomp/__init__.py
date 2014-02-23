# -*- coding: utf-8 -*-
import tempfile
import os
import glob
import subprocess
from utils import tar_paths, untar_to_path, rmrf
from werkzeug.exceptions import NotFound
from flask import Flask, url_for, redirect, render_template, request, Response
import re
import shutil

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


def output_logs(out_dir, code, output):
    # Don't create the __precomp__ directory if logging is disabled
    if request.form.get("logging", 'True') == 'False':
        return

    log_dir = os.path.join(out_dir, "__precomp__")
    if not os.path.isdir(log_dir):
        os.mkdir(log_dir)

    names = ("out", "err")
    for i in range(2):
        if output[i]:
            with open(os.path.join(log_dir, "std{0}.txt".format(names[i])), 'a') as f:
                f.write(output[i].decode("utf-8"))
                f.write("====================================================\n")
                f.write("---------------Status code:{0:3d}----------------------".format(code))
                f.write("\n====================================================\n\n")


def system_call(args):
    try:
        p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret = p.communicate()
        return (p.returncode, ret)
    except EnvironmentError as e:
        return (255, (None, "Server error: {0} - {1}".format(type(e).__name__, e).encode("utf-8")))

def replace_ext(path, ext):
    """Replace the filename's extension"""
    name, _ = os.path.splitext(path)
    return "{0}.{1}".format(name, ext)

def get_targets(arg_name, defaults=None):
    files = request.form.getlist(arg_name)
    if not files:
        return defaults
    return files

processors = {}

def processor(lang):
    def decorate(func):
        processors[lang] = func
        return func
    return decorate

@processor('mirror')
def mirror_proc(in_dir, out_dir):
    """Just mirrors the input directory"""
    files = glob.glob(os.path.join(in_dir, "*"))
    code, output = system_call(["cp", "-vr"] + files + [out_dir])
    output_logs(out_dir, code, output)
    return code != 0

@processor('sass')
@processor('scss')
def sass_proc(in_dir, out_dir):
    """Compiles (sass|scss) files in the input directory"""

    ret = True

    files = get_targets("targets")
    if files:
        # Compile all files specified
        for f in files:
            code, output = system_call(("sass", os.path.join(in_dir, f), os.path.join(out_dir, replace_ext(f, "css"))))
            output_logs(out_dir, code, output)
            ret = ret and code == 0
    else:
        # Compile everything in the directory
        code, output = system_call(("sass", in_dir, out_dir))
        output_logs(out_dir, code, output)
        ret = code == 0

    return ret


@processor('less')
def less_proc(in_dir, out_dir):
    """compiles main.less in the input directory"""

    ret = True

    for f in get_targets("targets", ("styles.less",)):
        code, output = system_call(("lessc", os.path.join(in_dir, f), os.path.join(out_dir, replace_ext(f, "css"))))
        output_logs(out_dir, code, output)
        ret = ret and code == 0

    return ret

@processor('gccmake')
def gccmake_proc(in_dir, out_dir):
    """Run make in the input directory"""
    MAKEFILE = "makefile"

    cwd = os.getcwd()
    os.chdir(in_dir)
    code, output = system_call(("make",))
    os.chdir(cwd)

    if code != 0:
        output_logs(out_dir, code, output)
        return False

    files = get_targets("targets")
    if not files:
        # No files specified, use makefile to try to determine the file(s) the user wants
        with open(os.path.join(in_dir, MAKEFILE), 'r') as mkfile:
            files = re.findall('-o\s+(\S+)', mkfile.read())

    for filename in files:
        if os.path.exists(os.path.join(in_dir, filename)):
            shutil.copy2(os.path.join(in_dir, filename), os.path.join(out_dir, filename))

    return True

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

    status = False

    try:
        untar_to_path(request.files['data'], in_dir)

        # Compile the code
        status = (processors[processor])(in_dir, out_dir)

        stream = tar_paths(out_dir)
    finally:
        rmrf(in_dir)
        rmrf(out_dir)

    r = Response(stream, mimetype="application/gzip")
    if not status:
        r.headers.add('warning', "Compilation reported a failure")

    return r
