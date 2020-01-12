from dicomsort.gui.errors import throw_error, wx
from tests.shared import WxTestCase


class TestThrowError(WxTestCase):
    def test_defaults(self, mocker):
        mock = mocker.patch.object(wx.MessageDialog, 'ShowModal')
        message = 'msg'
        throw_error(message, parent=self.frame)

        mock.assert_called_once()
