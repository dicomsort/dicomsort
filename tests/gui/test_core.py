import dicomsort

from six.moves.urllib.parse import parse_qs

from dicomsort.gui import core
from dicomsort.gui.core import errors, CrashReporter, sys
from tests.shared import WxTestCase


class TestCrashReporter(WxTestCase):
    def test_constructor(self):
        reporter = CrashReporter(self.frame)
        reporter.Destroy()

    def test_valid_email(self):
        email = 'email@gmail.com'
        reporter = CrashReporter(self.frame)
        reporter.emailAddress.SetValue(email)

        assert reporter.ValidateEmail() == email

        reporter.Destroy()

    def test_invalid_email(self, mocker):

        mock = mocker.patch.object(errors, 'throw_error')
        reporter = CrashReporter(self.frame)
        reporter.emailAddress.SetValue('invalid')

        reporter.ValidateEmail()

        mock.assert_called_with('Please enter a valid email address', parent=reporter)

        reporter.Destroy()

    def test_report(self, mocker):
        mock = mocker.patch.object(core, 'urlopen')

        sys.platform = 'platform'

        reporter = CrashReporter(self.frame)
        reporter.Report()

        call_args = mock.call_args[0]

        assert call_args[0] == 'http://www.suever.net/software/dicomSort/bug_report.php'

        query_params = parse_qs(call_args[1])

        assert query_params['OS'][0] == 'platform'
        assert query_params['version'][0] == dicomsort.__version__
        assert query_params['email'][0] == 'None'

        reporter.Destroy()
