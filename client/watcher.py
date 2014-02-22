import threading
import time
import os

class Watcher(threading.Thread):

    def __init__(self, directory, interval=1):
        self.directory = directory
        self.interval = interval

        self.stop = threading.Event()

        self.past = set()

        threading.Thread.__init__(self, target=self.serve_forever)

    def watch(self):
        """Returns true if any files were added, removed, or modified"""

        self.curr = set()
        for dirpath, dirname, filenames in os.walk(self.directory):
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

    def start_watching(self, callback):
        self.callback = callback
        self.start()
    
    def stop_watching(self):
        """Stop watching"""
        self.stop.set()

    def serve_forever(self):
        """Watch the specified directory"""
        while not self.stop.is_set():
            if self.watch():
                self.callback()
            time.sleep(1)

