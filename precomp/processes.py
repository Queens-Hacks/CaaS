
import os
import re
import glob
import shutil
from precomp import system_call, processor, output_logs

@processor('mirror')
def mirror_proc(in_dir, out_dir):
    """Just mirrors the input directory"""
    files = glob.glob(os.path.join(in_dir, "*"))
    code, output = system_call(["cp", "-vr"] + files + [out_dir])
    output_logs(out_dir, code, output)
    return code

@processor('sass')
def sass_proc(in_dir, out_dir):
    """compiles main.sass in the input directory"""
    MAIN_SASS = "main.sass"
    OUTPUT_FILE = "main.css"

    code, output = system_call(("sass", os.path.join(in_dir, MAIN_SASS), os.path.join(out_dir, OUTPUT_FILE)))

    output_logs(out_dir, code, output)
    return code

@processor('scss')
def scss_proc(in_dir, out_dir):
    """compiles main.scss in the input directory"""
    MAIN_SCSS = "main.scss"
    OUTPUT_FILE = "main.css"

    code, output = system_call(("sass", os.path.join(in_dir, MAIN_SCSS), os.path.join(out_dir, OUTPUT_FILE)))

    output_logs(out_dir, code, output)
    return code

@processor('less')
def less_proc(in_dir, out_dir):
    """compiles main.less in the input directory"""
    MAIN_LESS = "main.less"
    OUTPUT_FILE = "main.css"

    code, output = system_call(("lessc", os.path.join(in_dir, MAIN_LESS), os.path.join(out_dir, OUTPUT_FILE)))

    output_logs(out_dir, code, output)
    return code

@processor('gccmake')
def gccmake_proc(in_dir, out_dir):
    """runs make in the input directory"""
    MAKEFILE = "makefile"

    os.chdir(in_dir)
    code, output = system_call(("make"))

    with open(os.path.join(in_dir, MAKEFILE), 'r') as mkfile:
        out_files = re.findall('(?<=-o)\s+\S+', mkfile.read())

    for filename in out_files:
        filename = filename.strip()
        if os.path.exists(os.path.join(in_dir, filename)):
            shutil.copy2(os.path.join(in_dir, filename), os.path.join(out_dir, filename))

    output_logs(out_dir, code, output)
