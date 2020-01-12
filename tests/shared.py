import wx


class WxTestCase:
    def setup(self):
        self.app = wx.App()
        self.frame = wx.Frame(None)
        self.frame.Show()

    def teardown(self):
        def _cleanup():
            for win in wx.GetTopLevelWindows():
                if win:
                    if isinstance(win, wx.Dialog) and win.IsModal():
                        win.EndModal(0)
                    else:
                        win.Close(force=True)

            wx.WakeUpIdle()

        timer = wx.PyTimer(_cleanup)
        timer.Start(100)
        self.app.MainLoop()
