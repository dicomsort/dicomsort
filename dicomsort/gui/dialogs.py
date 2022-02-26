import dicomsort
import platform
import traceback
import webbrowser
import wx

from enum import Enum
from typing import Dict
from urllib.parse import quote

from dicomsort.gui import icons
from dicomsort.gui.help import helpHTML
from dicomsort.gui.overrides import HtmlWindow
from wx.adv import AboutBox, AboutDialogInfo
from wx.lib.agw import hyperlink


meta = dicomsort.Metadata


class AboutDlg:

    def __init__(self, parent=None):
        self.info = AboutDialogInfo()
        self.info.SetIcon(icons.about.GetIcon())

        self.info.SetName(meta.pretty_name)
        self.info.SetVersion(meta.version)

        self.info.SetCopyright(meta.copyright)
        self.info.SetWebSite(meta.website)

        self.update_description()

        AboutBox(self.info, parent=parent)

    def update_description(self):
        description = ("      Program designed to sort DICOM images       \n" +
                       "     into directories based upon DICOM header     \n" +
                       "      information. The program also provides      \n" +
                       "       additional functionality such as the       \n" +
                       "anonymization of DICOM images for patient privacy.")

        self.info.SetDescription(description)


class CrashReporter(wx.Dialog):
    title: str = 'DICOM Sort Error'

    def __init__(self, parent, **kwargs):
        super(CrashReporter, self).__init__(
            parent, -1, self.title, size=(400, 400)
        )

        self.type = kwargs.pop('type', None)
        self.value = kwargs.pop('value', None)
        self._traceback = kwargs.pop('traceback', None)

        self.create()
        self.SetIcon(icons.main.GetIcon())

    def traceback(self) -> str:
        return '\n'.join(
            traceback.format_exception(self.type, self.value, self._traceback)
        )

    def body(self) -> str:
        return \
            '#### Describe the Issue:\n' \
            'A clear and concise description of what the bug is.\n\n' \
            '#### Expected Behavior:\n' \
            'What you expected to happen.\n\n' \
            '#### Steps to Reproduce:\n' \
            'How to reproduce the issue.\n\n' \
            '## Environment\n' \
            f'#### DICOM Sort Version:\n{meta.version}\n\n' \
            f'#### Operating System:\n{platform.system()} '\
            f'{platform.release()}\n\n' \
            '#### Traceback:\n' + \
            '```\n' + \
            self.traceback() + \
            '\n```\n'

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        text = ''.join([
            'Dicom Sort had a problem and crashed. ',
            'In order to help diagnose the problem, you can submit an ',
            'issue and include the traceback below:',
        ])

        static = wx.StaticText(self, -1, text)
        static.Wrap(380)
        vbox.Add(static, 0, wx.ALL, 10)

        comments = wx.TextCtrl(
            self, style=wx.TE_MULTILINE, value=self.traceback()
        )
        vbox.Add(comments, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        submit_button = wx.Button(self, -1, 'File Issue')
        submit_button.Bind(wx.EVT_BUTTON, self.on_file_issue)

        cancel_button = wx.Button(self, -1, 'Cancel')
        cancel_button.Bind(wx.EVT_BUTTON, self.on_cancel)

        hbox.Add(submit_button, 0, wx.RIGHT, 10)
        hbox.Add(cancel_button, 0, wx.RIGHT, 10)

        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT, 10)

        self.SetSizer(vbox)

    def on_file_issue(self, *_event):
        webbrowser.open(meta.issue_url + '?body=' + quote(self.body()))

    def close(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()

    def on_cancel(self, event):
        self.close(event)


class HelpDlg(wx.Dialog):
    def __init__(self, parent=None):

        super(HelpDlg, self).__init__(
            parent, -1, f'{meta.pretty_name} Help',
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        )

        html_ctrl = HtmlWindow(self, -1, size=(400, 200))

        html_ctrl.SetPage(helpHTML)
        irep = html_ctrl.GetInternalRepresentation()

        html_ctrl.SetSize((irep.GetWidth(), int(irep.GetHeight() / 4)))
        self.Show()

        self.SetClientSize(html_ctrl.GetSize())
        self.CenterOnParent(wx.BOTH)
        self.SetFocus()

        self.Bind(wx.EVT_CLOSE, self.close)

    def close(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()


class SeriesRemoveOptions(Enum):
    ORIGINAL = 1
    CUSTOM = 2
    CANCEL = 3


class SeriesRemoveWarningDialog(wx.Dialog):
    choice: SeriesRemoveOptions = SeriesRemoveOptions.CANCEL

    def __init__(self, parent=None, size=(300, 200), config=None):
        super(SeriesRemoveWarningDialog, self).__init__(
            parent, title='BLAH', size=size, style=wx.DEFAULT_DIALOG_STYLE
        )

        vbox = wx.BoxSizer(wx.VERTICAL)

        message = 'Are you sure you want to remove the default\n' \
                  'attribute SeriesDescription?\n\n' \
                  'This may cause filename conflicts unless you\n' \
                  'use the original filenames.'

        txt = wx.StaticText(self, -1, message, style=wx.ALIGN_CENTER)

        original_button = wx.Button(
            self, -1, 'Yes. Use original Filenames', size=(-1, 20)
        )

        custom_button = wx.Button(
            self, -1, 'Yes. Use Custom Filenames', size=(-1, 20)
        )
        cancel_button = wx.Button(self, -1, 'Cancel', size=(-1, 20))

        original_button.Bind(
            wx.EVT_BUTTON,
            lambda e: self.on_button(e, SeriesRemoveOptions.ORIGINAL)
        )

        custom_button.Bind(wx.EVT_BUTTON, lambda e: self.on_button(e, SeriesRemoveOptions.CUSTOM))
        cancel_button.Bind(wx.EVT_BUTTON, lambda e: self.on_button(e, SeriesRemoveOptions.CANCEL))

        vbox.Add(txt, 1, wx.ALL | wx.ALIGN_CENTER, 10)
        vbox.Add(original_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        vbox.Add(custom_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        vbox.Add(cancel_button, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.SetSizer(vbox)

    def close(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()

    def on_button(self, event, choice: SeriesRemoveOptions):
        self.choice = choice
        self.close(event)


class QuickRenameDialog(wx.Dialog):

    def __init__(self, *args, **kwargs):
        anon_list = kwargs.pop('anonList')

        super(QuickRenameDialog, self).__init__(*args, **kwargs)

        self.anon_list = anon_list

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.values = self.anon_list.GetReplacementDict()
        initial_value = self.values.get('PatientName', '')

        txt = wx.StaticText(self, -1, 'PatientName')
        vbox.Add(txt, 0, wx.TOP | wx.ALIGN_CENTER, 15)

        self.patient_name_text = wx.TextCtrl(
            self, -1, initial_value, size=(200, 20), style=wx.TE_PROCESS_ENTER
        )

        self.Bind(wx.EVT_TEXT_ENTER, self.on_accept, self.patient_name_text)

        vbox.Add(self.patient_name_text, 0, wx.TOP | wx.ALIGN_CENTER, 5)

        self.use_as_patient_id = wx.CheckBox(self, -1, 'Use as Patient ID')
        self.use_as_patient_id.SetValue(True)

        vbox.Add(self.use_as_patient_id, 0, wx.TOP | wx.ALIGN_CENTER, 10)

        ok_button = wx.Button(self, -1, 'Ok')
        ok_button.Bind(wx.EVT_BUTTON, self.on_accept)

        vbox.Add(ok_button, 0, wx.TOP | wx.ALIGN_CENTER, 15)

        self.SetSizer(vbox)

        self.patient_name_text.SetFocus()

    def get_values(self) -> Dict[str, str]:
        result = {'PatientName': self.patient_name_text.GetValue()}

        if self.use_as_patient_id.IsChecked():
            result['PatientID'] = '%(PatientName)s'

        return result

    def on_accept(self, *event):
        replacements = self.anon_list.GetReplacementDict()
        replacements.update(self.get_values())
        self.anon_list.SetReplacementDict(replacements)
        self.close(event)

    def close(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()


class UpdateDialog(wx.Dialog):
    def __init__(self, parent, version):
        super(UpdateDialog, self).__init__(parent, size=(300, 170), style=wx.OK)

        message = f'A new version of {meta.pretty_name} is available.\n'\
                  f'You are running Version {dicomsort.__version__} and '\
                  f'the newest is {version}.'

        vbox = wx.BoxSizer(wx.VERTICAL)

        head = wx.StaticText(
            self, -1, label='Update Available', style=wx.ALIGN_CENTER
        )
        head.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        vbox.Add(head, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)

        message_ctrl = wx.StaticText(self, -1, label=message, style=wx.ALIGN_CENTER)
        vbox.Add(message_ctrl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.hyperlink = hyperlink.HyperLinkCtrl(self, -1)
        self.hyperlink.SetURL(URL=meta.website)
        self.hyperlink.SetLabel(label='Click here to obtain the update')
        self.hyperlink.SetToolTip(meta.website)
        self.hyperlink.AutoBrowse(False)

        self.Bind(hyperlink.EVT_HYPERLINK_LEFT, self.on_update, self.hyperlink)

        vbox.Add(self.hyperlink, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        ok_button = wx.Button(self, -1, 'OK')
        vbox.Add(ok_button, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)
        self.Bind(wx.EVT_BUTTON, self.close, ok_button)

        self.SetSizer(vbox)
        self.CenterOnParent()

    def close(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()

    def on_update(self, *event):
        self.hyperlink.GotoURL(self.hyperlink.GetURL())
        self.close(event)
