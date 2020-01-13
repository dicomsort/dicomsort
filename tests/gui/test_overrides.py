from dicomsort.gui.overrides import MultiDirDlg
from tests.shared import WxTestCase


class TestMultiDirDlg(WxTestCase):
    def test_constructor(self):
        dlg = MultiDirDlg(self.frame)
        assert isinstance(dlg, MultiDirDlg)

        dlg.Destroy()
