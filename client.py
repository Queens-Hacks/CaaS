import atexit
import sys
from client.manager import Manager

if __name__ == "__main__":
    if len(sys.argv) > 1:
        config = sys.argv[1]
    else:
        config = "client/config.yaml"
    m = Manager(config)
    m.start_watching()

@atexit.register
def on_exit():
    if m:
        m.stop_watching()
