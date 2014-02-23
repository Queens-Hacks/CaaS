import queue
import threading
import requests
import os
from utils import untar_stream_to_path, rmrf

class Service(object):

    URL = "http://localhost:5000/{0}"

    def __init__(self):
        """In the future sign into the API"""

        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self.serve_forever)
        self.worker.start()

    def process(self, conf, stream, callback):
        """Adds an request to the queue"""

        self.queue.put_nowait((conf, stream, callback))

    def shutdown(self):
        # Put a 'poison job' in the queue
        self.queue.put_nowait(None)

    def join(self):
        self.worker.join()

    def send(self, service, stream):
        r = requests.post(self.URL.format(service), files={"data": stream})
        if not r.ok:
            return None
        else:
            return r.content

    def extract_response(self, content, out_dir):
        if content is None:
            return

        # Create output dir if needed
        if not os.path.isdir(out_dir):
            try:
                os.mkdir(out_dir)
            except EnvironmentError as e:
                print ("Cannot create output folder '{0}': {1}".format(out_dir, str(e)))
        else:
            # Delete existing __precomp__ folder
            rmrf(os.path.join(out_dir, "__precomp__"))

        untar_stream_to_path(content, out_dir)

    def serve_forever(self):
        """Sends the data in the stream to the compilation service"""
        while True:
            temp = self.queue.get()

            # Check if 'poisoned'
            if temp is None:
                return

            conf, stream, callback = temp

            try:
                content = self.send(conf['type'], stream)
                self.extract_response(content, conf['output'])
            finally:
                # Make sure to always call the callback
                callback()
