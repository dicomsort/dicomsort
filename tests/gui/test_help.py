from dicomsort.gui.help import HtmlWindow, HelpDlg
from tests.shared import DialogTestCase


class TestHelpDialog(DialogTestCase):
    def test_constructor(self):
        self.dlg = HelpDlg(self.frame)
        assert isinstance(self.dlg.hwin, HtmlWindow)
