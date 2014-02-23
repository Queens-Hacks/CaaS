import threading
import time
import os
from utils import tar_paths

class Watcher(threading.Thread):

    def __init__(self, name, conf, service):
        self.name_ = name
        self.conf = conf
        self.service = service

        self.stop = threading.Event()
        self.lock = threading.Lock()
        self.past = set()

        threading.Thread.__init__(self, target=self.serve_forever)

    def watch(self):
        """Returns true if any files were added, removed, or modified"""

        self.curr = set()
        if not os.path.exists(self.conf['input']):
            raise Exception("{0}: File/folder '{1}' does not exist".format(self.name_, self.conf['input']))

        if not os.path.isdir(self.conf['input']):
            # Only checking a single file
            self.curr.add(os.path.getmtime(self.conf['input']))
        else:
            # Checking an entire directory
            for dirpath, dirname, filenames in os.walk(self.conf['input']):
                for f in filenames:
                    path = os.path.join(dirpath, f)

                    # Only store time modified
                    self.curr.add(os.path.getmtime(path))

        # If any times change between checks (not including order)
        # a file was either added, removed, or modified.
        if set(self.curr) != set(self.past):
            self.past = self.curr
            return True

        return False

    def shutdown(self):
        """Stop watching"""
        self.stop.set()

    def serve_forever(self):
        """Watch the specified directory"""
        while not self.stop.is_set():
            if self.watch():
                print ("{0}: Files changed, recompiling...".format(self.name_))
                stream = tar_paths(self.conf['input'])
                if stream is None:
                    print ("{0}: ERROR: Failed to pack files".format(self.name_))
                else:
                    self.lock.acquire()
                    self.service.process(self.conf, stream, self.unlock)

                    # Wait until the job is processed before continuing
                    self.lock.acquire()
                    self.lock.release()
            time.sleep(2)

    def unlock(self, msg):
        print ("{0}: {1}".format(self.name_, msg))
        self.lock.release()
