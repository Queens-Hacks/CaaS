import os
import re
import glob
import shutil
from precomp import system_call, processor, output_logs, replace_ext, get_targets


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

    output_logs(out_dir, code, output)

    if code != 0:
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


@processor('coffee')
def less_proc(in_dir, out_dir):
    """compiles main.less in the input directory"""

    code, output = system_call(("coffee", "-c", "-o", out_dir, in_dir))

    output_logs(out_dir, code, output)

    return code == 0
