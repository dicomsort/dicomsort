from dicomsort.gui.help import HtmlWindow, HelpDlg


class TestHelpDialog():
    def teardown(self):
        self.dlg.close()

    def test_constructor(self, app):
        self.dlg = HelpDlg()
        assert isinstance(self.dlg.hwin, HtmlWindow)
