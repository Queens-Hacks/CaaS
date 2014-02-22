import os
import io
import zipfile
import logging
import time
import atexit

from service import Service
from watcher import Watcher


class Client(object):

    def __init__(self, service, directory = "."):
        self.service = service
        self.directory = directory
        self.s = Service(self.service)
        self.w = Watcher(self.directory)

    def start_watching(self):
        """Start the watcher"""
        self.w.start_watching(self.on_change)
        print ("Watching directory {0}. Press Ctrl+C t exit")

    def stop_watching(self):
        """Start the watcher and return"""
        print ("Stopping the watch service...")
        self.w.stop_watching()
        self.w.join()
        print ("Stopped!")

    def on_change(self):
        """
        Called by the watcher when something in the 
        watched directory is modified
        """
        stream = zip_paths(self.directory)
        self.s.send(stream)


def zip_paths(paths):
    """
    Compresses directories and files to a single zip file.
    
    Returns the zip file as a data stream, None if error.
    """
    # Check single path vs. multiple
    if isinstance(paths, str):
        paths = (paths,)

    # Filter out non-existent paths
    paths = [x for x in paths if os.path.exists(x)]

    # Make sure the zip file will actually contain something
    if not paths:
        logging.warning("No files/folders to add, not creating zip file")
        return None

    logging.debug("Creating zip file")
    zip_stream = io.BytesIO()
    try:
        zfile = zipfile.ZipFile(zip_stream, 'w', compression=zipfile.ZIP_DEFLATED)
    except EnvironmentError as e:
        logging.warning("Couldn't create zip file")
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
                        zfile.write(fullpath, archive_name, zipfile.ZIP_DEFLATED)
                    except EnvironmentError as e:
                        logging.warning("Couldn't add file: %s", (str(e),))
        else:
            # Exists and not a directory, assume a file
            try:
                zfile.write(path, os.path.basename(path), zipfile.ZIP_DEFLATED)
            except EnvironmentError as e:
                logging.warning("Couldn't add file: %s", (str(e),))
    zfile.close()
    zip_stream.seek(0)

    return zip_stream

if __name__ == "__main__":
    c = Client("less", ".")
    c.start_watching()

@atexit.register
def on_exit():
    if c:
        c.stop_watching()
