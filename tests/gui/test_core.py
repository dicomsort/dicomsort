import dicomsort
import sys

from dicomsort.gui import core
from dicomsort.gui.core import errors, CrashReporter


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

        self.reporter = CrashReporter()
        self.reporter.Report()

        params = "version={}&OS={}&email=None&comments=--------------DO+NOT+EDIT+BELOW+------------%0ANone".format(dicomsort.__version__, sys.platform)
        mock.assert_called_with('http://www.suever.net/software/dicomSort/bug_report.php', params)
