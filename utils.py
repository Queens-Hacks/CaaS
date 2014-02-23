import os
import io
import tarfile
import logging
import shutil


def tar_paths(paths):
    """
    Compresses directories and files to a single tar file.

    Returns the tar file as a data stream, None if error.
    """
    # Check single path vs. multiple
    if isinstance(paths, str):
        paths = (paths,)

    # Filter out non-existent paths
    paths = [x for x in paths if os.path.exists(x)]

    # Make sure the tar file will actually contain something
    if not paths:
        logging.warning("No files/folders to add, not creating tar file")
        return None

    logging.debug("Creating tar file")
    tar_stream = io.BytesIO()
    try:
        zfile = tarfile.open(fileobj=tar_stream, mode='w|gz')
    except EnvironmentError as e:
        logging.warning("Couldn't create tar file")
        return None

    for path in paths:
        if os.path.isdir(path):
            root_len = len(os.path.abspath(path))

            # If compressing multiple things, preserve the top-level folder names
            if len(paths) > 1:
                root_len -= len(os.path.basename(path)) + len(os.sep)

            # Walk through the directory, adding all files
            for root, dirs, files in os.walk(path):
                archive_root = os.path.abspath(root)[root_len:]
                for f in files:
                    fullpath = os.path.join(root, f)
                    archive_name = os.path.join(archive_root, f)
                    try:
                        zfile.add(fullpath, archive_name, recursive=False)
                    except EnvironmentError as e:
                        logging.warning("Couldn't add file: %s", (str(e),))
        else:
            # Exists and not a directory, assume a file
            try:
                zfile.add(path, os.path.basename(path),  recursive=False)
            except EnvironmentError as e:
                logging.warning("Couldn't add file: %s", (str(e),))
    zfile.close()
    tar_stream.seek(0)

    return tar_stream

def untar_to_path(zfile, target):

    with tarfile.open(fileobj=zfile, mode='r') as zfile:
        zfile.extractall(path=target)

def untar_stream_to_path(stream, target):
    zfile = io.BytesIO(stream)
    untar_to_path(zfile, target)


def rmrf(path):
    """Just delete it, dude"""

    if os.path.isdir(path):
        shutil.rmtree(path)
    elif os.path.exists(path):
        os.remove(path)
