import dicomsort
import os
import sys

from urllib.parse import parse_qs, urlparse

from dicomsort.gui.anonymizer import AnonymizeList
from dicomsort.gui.dialogs import (
    AboutDlg,
    CrashReporter,
    QuickRenameDlg,
    SeriesRemoveWarningDlg,
    UpdateDlg,
    webbrowser,
)
from tests.shared import WxTestCase


class TestCrashReporter(WxTestCase):
    def test_constructor(self):
        reporter = CrashReporter(self.frame)
        reporter.Destroy()

    def test_body(self):
        # Given an exception and a traceback
        try:
            raise AttributeError('oh no')
        except AttributeError:
            pass

        t, v, tb = sys.exc_info()

        # And a CrashReporter corresponding to this exception
        reporter = CrashReporter(self.frame, type=t, value=v, traceback=tb)

        # The body generated by the Crash Reporter
        body = reporter.body()

        # Has the expected information
        assert dicomsort.__version__ in body

        platform = ' '.join(os.uname())
        assert platform in body

        assert reporter.traceback() in body

    def test_on_file(self, mocker):
        mock = mocker.patch.object(webbrowser, 'open')
        reporter = CrashReporter(self.frame)

        reporter.on_file()

        assert mock.call_count == 1

        url = mock.call_args[0][0]

        parsed_url = urlparse(url)

        assert parsed_url.scheme == 'https'
        assert parsed_url.netloc == 'github.com'
        assert parsed_url.path == '/suever/dicomsort/issues/new'

        query_params = parse_qs(parsed_url.query)

        assert 'body' in query_params
        assert query_params['body'][0] == reporter.body()


class TestUpdateDlg(WxTestCase):
    def test_on_close(self):
        dlg = UpdateDlg(self.frame, '1.2.3')
        dlg.OnClose()

    def test_on_update(self, mocker):
        dlg = UpdateDlg(self.frame, '1.2.3')
        url = dicomsort.__website__

        mock = mocker.patch.object(dlg.link, 'GotoURL')

        dlg.OnUpdate()

        mock.assert_called_once_with(url)


class TestAboutDialog(WxTestCase):
    def test_constructor(self):
        dlg = AboutDlg(self.frame)

        # Just a few sanity checks
        assert dlg.info.GetVersion() == dicomsort.__version__
        assert dlg.info.GetName() == 'DICOM Sorting'
        assert dlg.info.GetWebSiteURL() == dicomsort.__website__


class TestSeriesRemoveWarningDlg(WxTestCase):
    def test_on_change(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnChange()

        assert dlg.choice == 1

    def test_on_cancel(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnCancel()

        assert dlg.choice == 0

    def test_on_accept(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnAccept()

        assert dlg.choice == 2


class TestQuickRenameDlg(WxTestCase):
    def test_no_patient_name_anonlist(self):
        a = AnonymizeList(self.frame)
        dlg = QuickRenameDlg(self.frame, anonList=a)

        expected = {
            'PatientName': '',
            'PatientID': '%(PatientName)s',
        }

        assert dlg.GetValues() == expected

    def test_patient_name_anonlist(self):
        name = 'Patient0'
        a = AnonymizeList(self.frame)
        a.SetStringItems(['PatientName'])
        a.SetReplacementDict({'PatientName': name})

        dlg = QuickRenameDlg(self.frame, anonList=a)

        expected = {
            'PatientName': name,
            'PatientID': '%(PatientName)s',
        }

        assert dlg.GetValues() == expected

    def test_on_accept(self):
        name = 'Patient0'
        a = AnonymizeList(self.frame)
        a.SetStringItems(['PatientName', 'PatientID'])
        a.SetReplacementDict({'PatientName': name, 'PatientID': 'ignored'})

        dlg = QuickRenameDlg(self.frame, anonList=a)

        dlg.OnAccept()

        assert a.GetReplacementDict()['PatientID'] == '%(PatientName)s'
        assert a.GetReplacementDict()['PatientName'] == name
