
class Service(object):

    SERVICES = (
        "coffescript",
        "sass",
        "scss",
        "less",
        "haml",
    )

    def __init__(self, service):
        """Do nothing for now, but in the future sign into the API"""
        if not service in self.SERVICES:
            raise Exception("'{0}' is not a valid service type".format(service))
        self.service = service

    def send(self, stream):
        """Sends the data in the stream to the compilation service"""
        print (stream)

