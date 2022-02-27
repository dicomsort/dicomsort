from dicomsort.gui.dialogs import HelpDlg
from dicomsort.gui.overrides import HtmlWindow
from tests.shared import WxTestCase


class TestHelpDialog(WxTestCase):
    def test_constructor(self):
        self.dlg = HelpDlg(self.frame)

