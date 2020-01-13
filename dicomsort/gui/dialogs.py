import dicomsort
import os
import traceback
import webbrowser
import wx

from dicomsort.gui import icons
from six.moves.urllib.parse import quote


class CrashReporter(wx.Dialog):
    TITLE = 'DICOM Sort Error'
    ISSUE_URL = 'https://github.com/suever/dicomsort/issues/new'

    ISSUE_TEMPLATE = '**Traceback:**\n'

    def __init__(self, parent, **kwargs):
        super(CrashReporter, self).__init__(
            parent, -1, self.TITLE, size=(400, 400)
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
        ver = dicomsort.__version__

        template = \
            '#### Describe the Issue:\n' + \
            'A clear and concise description of what the bug is.\n\n' + \
            '#### Expected Behavior:\n' + \
            'What you expected to happen.\n\n' + \
            '#### Steps to Reproduce:\n' + \
            'How to reproduce the issue.\n\n' + \
            '## Environment\n' + \
            '#### DICOM Sort Version:\n{}\n\n'.format(ver) + \
            '#### Operating System:\n{}\n\n'.format(' '.join(os.uname())) + \
            '#### Traceback:\n' + \
            '```\n' + \
            self.traceback() + \
            '\n```\n'

        return template

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        text = ''.join([
            'Dicom Sorting had a problem and crashed. ',
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
        webbrowser.open(self.ISSUE_URL + '?body=' + quote(self.body()))

    def on_button(self, event):
        if self.IsModal():
            self.EndModal(event.EventObject.Id)
        else:
            self.Close()
