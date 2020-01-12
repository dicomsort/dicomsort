import wx


def throw_error(message, title='Error', parent=None):
    """
    Generic way to throw an error and display the appropriate dialog
    """
    dlg = wx.MessageDialog(parent, message, title, wx.OK | wx.ICON_ERROR)
    dlg.CenterOnParent()
    dlg.ShowModal()
    dlg.Destroy()
