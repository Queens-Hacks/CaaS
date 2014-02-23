import queue
import threading
import requests
from utils import untar_stream_to_path

class Service(object):

    URL = "http://localhost:5000/{0}"

    SERVICES = (
        "coffescript",
        "sass",
        "scss",
        "less",
        "haml",
    )

    def __init__(self):
        """In the future sign into the API"""

        self.queue = queue.Queue()
        self.worker = threading.Thread(target=self.serve_forever)
        self.worker.start()

    def process(self, conf, stream, callback):
        """Adds an request to the queue"""
        if not conf['type'] in self.SERVICES:
            raise Exception("'{0}' is not a valid service type".format(conf['type']))

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
                if content is not None:
                    untar_stream_to_path(content, conf['output'])
            finally:
                # Make sure to always call the callback
                callback()
