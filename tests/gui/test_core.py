import dicomsort

from six.moves.urllib.parse import parse_qs

from dicomsort.gui import core
from dicomsort.gui.core import errors, CrashReporter, sys


class TestCrashReporter:
    def teardown(self):
        self.reporter.Destroy()

    def test_constructor(self, app):
        self.reporter = CrashReporter()

    def test_valid_email(self, app):
        email = 'email@gmail.com'
        self.reporter = CrashReporter()
        self.reporter.emailAddress.SetValue(email)

        assert self.reporter.ValidateEmail() == email

    def test_invalid_email(self, app, mocker):

        mock = mocker.patch.object(errors, 'throw_error')
        self.reporter = CrashReporter()
        self.reporter.emailAddress.SetValue('invalid')

        self.reporter.ValidateEmail()

        mock.assert_called_with('Please enter a valid email address', parent=self.reporter)

    def test_report(self, app, mocker):
        mock = mocker.patch.object(core, 'urlopen')

        sys.platform = 'platform'

        self.reporter = CrashReporter()
        self.reporter.Report()

        call_args = mock.call_args[0]

        assert call_args[0] == 'http://www.suever.net/software/dicomSort/bug_report.php'

        query_params = parse_qs(call_args[1])

        assert query_params['OS'][0] == 'platform'
        assert query_params['version'][0] == dicomsort.__version__
        assert query_params['email'][0] == 'None'
