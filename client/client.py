from client.service import Service
from client.watcher import Watcher

import yaml

class Client(object):

    def __init__(self, config):

        with open(config, "r") as f:
            config = yaml.load(f.read())

        self.s = Service()

        self.watchers = []
        for k, v in config.items():
            self.watchers.append(Watcher(v, self.s))

    def start_watching(self):
        """Start the watchers"""
        print ("Starting watchers. Press Ctrl+C to exit")
        for x in self.watchers:
            x.start()

    def stop_watching(self):
        """Start the watcher and return"""
        print ("Stopping the watching services...")

        for x in self.watchers:
            x.shutdown()
        
        self.s.shutdown()
        
        for x in self.watchers:
            x.join()

        self.s.join()

        print ("Stopped!")
