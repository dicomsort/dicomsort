import dicomsort
import re
import wx

from threading import Thread
from six.moves.urllib.request import urlopen

from dicomsort.gui import events

VERSION_URL = "http://www.dicomsort.com/current"


def version_tuple(version):
    parts = list()

    for component in version.split('.'):
        number_match = re.match('^\\d+', component)

        if number_match is None:
            continue

        parts.append(int(number_match.group()))

    return tuple(parts)


VERSION_TUPLE = version_tuple(dicomsort.__version__)


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
    latest_version_tuple = version_tuple(latest)
    for ind in range(len(latest_version_tuple)):
        if latest_version_tuple[ind] > VERSION_TUPLE[ind]:
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
