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

    def extract_response(self, response, out_dir):
        if response.content is None:
            return "ERROR: No content recieved"

        # Create output dir if needed
        if not os.path.isdir(out_dir):
            try:
                os.mkdir(out_dir)
            except EnvironmentError as e:
                return "ERROR: Cannot create output folder '{0}': {1}".format(out_dir, str(e))
        else:
            # Delete existing __precomp__ folder
            rmrf(os.path.join(out_dir, "__precomp__"))

        untar_stream_to_path(response.content, out_dir)
        warn = response.headers.get('warning', None)
        if warn:
            return "WARNING: '{0}'. Finished, new files in '{1}'".format(warn, out_dir)
        else:
            return "Compilation succeeded, new files in '{0}'".format(out_dir)

    def serve_forever(self):
        """Sends the data in the stream to the compilation service"""
        while True:
            temp = self.queue.get()

            # Check if 'poisoned'
            if temp is None:
                return

            conf, stream, callback = temp

            try:
                msg = "ERROR: Couldn't communicate properly with the server"
                r = requests.post(self.URL.format(conf['type']), files={"data": stream}, data=conf['extras'])
                if r.ok:
                    msg = "ERROR: Failed to extract the response from the server"
                    msg = self.extract_response(r, conf['output'])
                else:
                    msg = "HTTP ERROR {0}: {1}".format(r.status_code, r.text)
            except EnvironmentError as e:
                pass
            finally:
                # Make sure to always call the callback
                callback(msg)
