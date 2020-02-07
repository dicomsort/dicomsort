import wx

from threading import Thread

from dicomsort.gui import events
from dicomsort.update import update_available


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
