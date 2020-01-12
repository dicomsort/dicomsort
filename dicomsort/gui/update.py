import dicomsort
import wx

from threading import Thread
from six.moves.urllib.request import urlopen

from dicomsort.gui import events

VERSION_TUPLE = tuple([int(x) for x in dicomsort.__version__.split('.')])
VERSION_URL = "http://www.dicomsort.com/current"


def latest_version():
    try:
        f = urlopen(VERSION_URL)
        version = f.read().rstrip()

        if '404' in version:
            return None

        return version
    except IOError:
        return None


def update_available():
    # First try to see if we can connect
    latest = latest_version()

    if latest is None or latest == dicomsort.__version__:
        return None

    # Break it up to see if it's a dev version
    I = [int(part) for part in latest.split('.')]
    for ind in range(len(I)):
        if I[ind] > VERSION_TUPLE[ind]:
            return latest
        return None


class UpdateChecker(Thread):

    def __init__(self, frame, listener):
        self.frame = frame
        self.listener = listener

        Thread.__init__(self)
        self.name = 'UpdateThread'

        # Make it a daemon so that when the MainThread exits, it is terminated
        self.daemon = True
        self.start()

    def run(self):
        version = update_available()

        if version:
            print('Current Version is %s' % version)
            # Send an event to the main thread to tell them
            event = events.UpdateEvent(version=version)
            wx.PostEvent(self.listener, event)
