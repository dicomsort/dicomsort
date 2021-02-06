import dicomsort
import os
import traceback
import webbrowser
import wx

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

        self.GenerateDescription()

        AboutBox(self.info, parent=parent)

    def GenerateDescription(self):
        description = ("      Program designed to sort DICOM images       \n" +
                       "     into directories based upon DICOM header     \n" +
                       "      information. The program also provides      \n" +
                       "       additional functionality such as the       \n" +
                       "anonymization of DICOM images for patient privacy.")

        self.info.SetDescription(description)


class CrashReporter(wx.Dialog):
    title = 'DICOM Sort Error'

    def __init__(self, parent, **kwargs):
        super(CrashReporter, self).__init__(
            parent, -1, self.title, size=(400, 400)
        )

        self.type = kwargs.pop('type', None)
        self.value = kwargs.pop('value', None)
        self._traceback = kwargs.pop('traceback', None)

        self.create()
        self.SetIcon(icons.main.GetIcon())

    def traceback(self):
        lines = traceback.format_exception(type, self.value, self._traceback)
        return '\n'.join(lines)

    def body(self):
        return \
            '#### Describe the Issue:\n' + \
            'A clear and concise description of what the bug is.\n\n' + \
            '#### Expected Behavior:\n' + \
            'What you expected to happen.\n\n' + \
            '#### Steps to Reproduce:\n' + \
            'How to reproduce the issue.\n\n' + \
            '## Environment\n' + \
            '#### DICOM Sort Version:\n{}\n\n'.format(meta.version) + \
            '#### Operating System:\n{}\n\n'.format(' '.join(os.uname())) + \
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

        value = '\n'.join(
            traceback.format_exception(type, self.value, self._traceback)
        )
        self.comments = wx.TextCtrl(self, style=wx.TE_MULTILINE, value=value)
        vbox.Add(self.comments, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.submit = wx.Button(self, -1, 'File Issue')
        self.submit.Bind(wx.EVT_BUTTON, self.on_file)

        self.done = wx.Button(self, -1, 'Done')
        self.done.Bind(wx.EVT_BUTTON, self.on_button)

        hbox.Add(self.submit, 0, wx.RIGHT, 10)
        hbox.Add(self.done, 0, wx.RIGHT, 10)

        vbox.Add(hbox, 0, wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT, 10)

        self.SetSizer(vbox)

    def on_file(self, *_event):
        webbrowser.open(meta.issue_url + '?body=' + quote(self.body()))

    def on_button(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()


class HelpDlg(wx.Dialog):

    def __init__(self, parent=None, **kwargs):

        super(HelpDlg, self).__init__(
            parent, -1, '{} Help'.format(meta.pretty_name),
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        )

        self.hwin = HtmlWindow(self, -1, size=(400, 200))

        self.hwin.SetPage(helpHTML)
        irep = self.hwin.GetInternalRepresentation()

        self.hwin.SetSize((irep.GetWidth(), int(irep.GetHeight() / 4)))
        self.Show()

        self.SetClientSize(self.hwin.GetSize())
        self.CenterOnParent(wx.BOTH)
        self.SetFocus()

        self.Bind(wx.EVT_CLOSE, self.close)

    def close(self, *_):
        self.Destroy()


class SeriesRemoveWarningDlg(wx.Dialog):

    def __init__(self, parent, id=-1, size=(300, 200), config=None):
        wx.Dialog.__init__(
            self, parent, id, 'Remove Series Description?', size=size
        )

        vbox = wx.BoxSizer(wx.VERTICAL)

        inputText = ''.join(['Are you sure you want to remove the default\n',
                             'attribute SeriesDescription?\n\n',
                             'This may cause filename conflicts unless you\n',
                             'use the original filenames.'])

        txt = wx.StaticText(self, -1, inputText, style=wx.ALIGN_CENTER)

        change = wx.Button(
            self, -1, 'Yes. Use original Filenames', size=(-1, 20)
        )

        accept = wx.Button(
            self, -1, 'Yes. Use Custom Filenames', size=(-1, 20)
        )
        cancel = wx.Button(self, -1, 'Cancel', size=(-1, 20))

        change.Bind(wx.EVT_BUTTON, self.OnChange)
        accept.Bind(wx.EVT_BUTTON, self.OnAccept)
        cancel.Bind(wx.EVT_BUTTON, self.OnCancel)

        self.Bind(wx.EVT_CLOSE, self.OnCancel)

        vbox.Add(txt, 1, wx.ALL | wx.ALIGN_CENTER, 10)
        vbox.Add(change, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        vbox.Add(accept, 0, wx.ALL | wx.ALIGN_CENTER, 5)
        vbox.Add(cancel, 0, wx.ALL | wx.ALIGN_CENTER, 5)

        self.SetSizer(vbox)

        self.Destroy()

    def OnChange(self, *evnt):
        self.choice = 1
        self.Destroy()

    def OnCancel(self, *evnt):
        self.choice = 0
        self.Destroy()

    def OnAccept(self, *evnt):
        self.choice = 2
        self.Destroy()


class QuickRenameDlg(wx.Dialog):

    def __init__(self, *args, **kwargs):
        tmp = kwargs.pop('anonList')
        wx.Dialog.__init__(self, *args, **kwargs)
        self.anonList = tmp
        self.values = dict()

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.values = self.anonList.GetReplacementDict()
        if 'PatientName' in self.values:
            initial = self.values['PatientName']
        else:
            initial = ''

        txt = wx.StaticText(self, -1, 'PatientName')
        vbox.Add(txt, 0, wx.TOP | wx.ALIGN_CENTER, 15)

        self.patientName = wx.TextCtrl(self, -1, initial, size=(200, 20),
                                       style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_TEXT_ENTER, self.OnAccept, self.patientName)

        vbox.Add(self.patientName, 0, wx.TOP | wx.ALIGN_CENTER, 5)

        self.samecheck = wx.CheckBox(self, -1, 'Use as Patient ID')
        self.samecheck.SetValue(True)

        vbox.Add(self.samecheck, 0, wx.TOP | wx.ALIGN_CENTER, 10)

        self.btnOK = wx.Button(self, -1, 'Ok')
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnAccept)

        vbox.Add(self.btnOK, 0, wx.TOP | wx.ALIGN_CENTER, 15)

        self.SetSizer(vbox)

        self.patientName.SetFocus()

    def GetValues(self):
        res = dict()
        res['PatientName'] = self.patientName.GetValue()

        if self.samecheck.IsChecked():
            res['PatientID'] = '%(PatientName)s'

        return res

    def OnAccept(self, *evnt):
        oldDict = self.anonList.GetReplacementDict()
        oldDict.update(self.GetValues())
        self.anonList.SetReplacementDict(oldDict)
        self.Close()


class UpdateDlg(wx.Dialog):
    def __init__(self, parent, version):
        super(UpdateDlg, self).__init__(parent, size=(300, 170), style=wx.OK)
        message = ''.join([
            'A new version of {} is available.\n'.format(meta.pretty_name),
            'You are running Version %s and the newest is %s.\n'
        ])

        vbox = wx.BoxSizer(wx.VERTICAL)

        head = wx.StaticText(
            self, -1, label='Update Available', style=wx.ALIGN_CENTER
        )
        head.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.BOLD))

        vbox.Add(head, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)

        txt = wx.StaticText(
            self, -1, label=message % (dicomsort.__version__, version),
            style=wx.ALIGN_CENTER)
        vbox.Add(txt, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.link = hyperlink.HyperLinkCtrl(self, -1)
        self.link.SetURL(URL=meta.website)
        self.link.SetLabel(label='Click here to obtain the update')
        self.link.SetToolTip(meta.website)
        self.link.AutoBrowse(False)

        self.Bind(hyperlink.EVT_HYPERLINK_LEFT, self.OnUpdate, self.link)

        vbox.Add(self.link, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 0)

        ok = wx.Button(self, -1, "OK")
        vbox.Add(ok, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 15)
        self.Bind(wx.EVT_BUTTON, self.OnClose, ok)

        self.SetSizer(vbox)
        self.CenterOnParent()

    def OnUpdate(self, *evnt):
        self.link.GotoURL(self.link.GetURL())
        self.Destroy()

    def OnClose(self, *evnt):
        self.Destroy()
