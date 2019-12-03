import dicomsort
import re
import urllib2
import wx

from threading import Thread

from dicomsort.gui import events

VERSION_TUPLE = tuple([int(x) for x in dicomsort.__version__.split('.')])


def AvailableUpdate():
    # First try to see if we can connect
    try:
        f = urllib2.urlopen("http://www.dicomsort.com/current")
        current = f.read().rstrip()
    except IOError:
        return None

    if re.search('404', current):
        return None

    if current == dicomsort.__version__:
        return None
    else:
        # Break it up to see if it's a dev version
        I = [int(part) for part in current.split('.')]
        for ind in range(len(I)):
            if I[ind] > VERSION_TUPLE[ind]:
                return current
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
        version = AvailableUpdate()

        if version:
            print('Current Version is %s' % version)
            # Send an event to the main thread to tell them
            event = events.UpdateEvent(version=version)
            wx.PostEvent(self.listener, event)
