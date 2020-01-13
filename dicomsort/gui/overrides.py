import wx

from wx import html
from wx.lib.agw import multidirdialog


class HtmlWindow(html.HtmlWindow):
    def __init__(self, parent, id, size):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()


class MultiDirDlg(multidirdialog.MultiDirDialog):
    """
    We have to over-ride this because of the IndexError on win7
    """

    def __init__(self, *args, **kwargs):
        super(MultiDirDlg, self).__init__(*args, **kwargs)

    def SetupDirCtrl(self, *args, **kwargs):
        try:
            super(MultiDirDlg, self).SetupDirCtrl(*args, **kwargs)
        except IndexError:
            self.folderText.SetValue('')
