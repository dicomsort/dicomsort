import wx
import wx.lib.newevent

configFile = 'dicomSort.ini'

# Define events
PathEvent,EVT_PATH = wx.lib.newevent.NewEvent()
PopulateEvent,EVT_POPULATE_FIELDS = wx.lib.newevent.NewEvent()

def ThrowError(message,titl = 'Error'):
    """
    Generic way to throw an error and display the appropriate dialog
    """
    dlg = wx.MessageDialog(None,message,title,wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


