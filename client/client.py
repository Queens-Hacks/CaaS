import atexit

from service import Service
from watcher import Watcher
from utils import zip_paths


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


if __name__ == "__main__":
    c = Client("less", ".")
    c.start_watching()

@atexit.register
def on_exit():
    if c:
        c.stop_watching()
