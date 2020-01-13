from dicomsort.gui.core import MainFrame, sys
from tests.shared import WxTestCase


class TestMainFrame(WxTestCase):
    def test_on_quit(self, mocker):
        mock = mocker.patch.object(sys, 'exit')
        frame = MainFrame(self.frame)
        frame.Show()

        frame.Close()

        # Ensure that the program was exited
        mock.assert_called_once_with(0)
