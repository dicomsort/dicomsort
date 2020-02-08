import mock
import wx

from dicomsort.gui import update
from tests.shared import WxTestCase


class TestUpdateChecker(WxTestCase):
    def test_no_update(self, mocker):
        mocker.patch.object(update, 'update_available', return_value=None)

        post_event_func = mocker.patch.object(wx, 'PostEvent')

        checker = update.UpdateChecker(self.frame, lambda x: x)

        # Wait for this thread to complete
        checker.join()

        post_event_func.assert_not_called()

    def test_update(self, mocker):
        version = '1.2.3'
        mocker.patch.object(update, 'update_available', return_value=version)

        post_event_func = mocker.patch.object(wx, 'PostEvent')

        def listener(*args):
            pass

        checker = update.UpdateChecker(self.frame, listener)

        # Wait for this thread to complete
        checker.join()

        post_event_func.assert_called_with(listener, mock.ANY)
