from dicomsort.gui.errors import throw_error, wx
from tests.shared import DialogTestCase


class TestThrowError(DialogTestCase):
    def test_defaults(self, mocker):
        mock = mocker.patch.object(wx.MessageDialog, 'ShowModal')
        message = 'msg'
        throw_error(message)

        mock.assert_called_once()