import dicomsort
import mock
import wx

from six.moves import StringIO

from dicomsort.gui import events, update
from tests.shared import WxTestCase


class TestLatestVersion:
    def test_healthy_endpoint(self, mocker):
        version = '1.2.3'
        mocker.patch.object(update, 'urlopen', return_value=StringIO(version))

        assert update.latest_version() == version

    def test_404_endpoint(self, mocker):
        mocker.patch.object(update, 'urlopen', return_value=StringIO('404 Page Not Found'))

        assert update.latest_version() is None

    def test_http_error(self, mocker):
        mocker.patch.object(update, 'urlopen', side_effect=IOError())

        assert update.latest_version() is None


class TestUpdateAvailable:
    def test_none_version(self, mocker):
        # When the latest version is not able to be found
        mocker.patch.object(update, 'latest_version', return_value=None)

        # No update is available
        assert update.update_available() is None

    def test_old_version(self, mocker):
        # When the latest version is older than the local version
        mocker.patch.object(update, 'latest_version', return_value='0.0.0')

        # No update is available
        assert update.update_available() is None

    def test_new_version(self, mocker):
        current = update.VERSION_TUPLE
        latest_version_tuple = [str(x) for x in (current[0] + 1, ) + current[1:]]
        latest_version = '.'.join(latest_version_tuple)
        mocker.patch.object(update, 'latest_version', return_value=latest_version)

        assert update.update_available() == latest_version

    def test_same_version(self, mocker):
        latest_version = dicomsort.__version__
        mocker.patch.object(update, 'latest_version', return_value=latest_version)

        assert update.update_available() is None


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
