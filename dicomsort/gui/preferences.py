import six
import wx
import wx.py
import configobj

from dicomsort import config
from dicomsort.gui.anonymizer import AnonymizeList


class PreferencePanel(wx.Panel):

    def __init__(self, parent, shortname, title, config):
        wx.Panel.__init__(self, parent, -1)
        self.shortname = shortname
        self.config = config
        self.title = title

    def GetState(self):
        raise TypeError('Abstract Method!')

    def SaveState(self, *evnt):
        # Load since last saved version
        tmpconfig = configobj.ConfigObj(self.config.filename)
        self.StoreState(config=tmpconfig)

        # Write just the change from this panel
        tmpconfig.write()

    def UpdateFromConfig(self, config=None):
        raise TypeError('Abstract Method!')

    def RevertState(self, *evnt):
        # Load a temporary copy
        tmpconfig = configobj.ConfigObj(self.config.filename)
        self.config[self.shortname] = tmpconfig[self.shortname]
        # TODO: See if all of these configobjs need to be closed()

    def StoreState(self, config=None):
        if config is None:
            config = self.config

        config[self.shortname] = self.GetState()


class MiscPanel(PreferencePanel):
    def __init__(self, parent, config):
        super(MiscPanel, self).__init__(parent, 'Miscpanel',
                                        'Miscellaneous', config)
        self.create()

    def GetState(self):
        return {
            'KeepSeries': str(self.keepSeries.IsChecked()),
            'SeriesFirst': str(self.seriesFirst.IsChecked()),
            'KeepOriginal': str(self.keepOriginal.IsChecked())
        }

    def RevertState(self, *evnt):
        super(MiscPanel, self).RevertState()
        savedConfig = configobj.ConfigObj(self.config.filename)
        self.UpdateFromConfig(savedConfig)

    def UpdateFromConfig(self, config):
        tmp = config[self.shortname]
        if 'KeepSeries' not in tmp:
            tmp['KeepSeries'] = 'True'

        if 'SeriesFirst' not in tmp:
            tmp['SeriesFirst'] = 'False'

        if 'KeepOriginal' not in tmp:
            tmp['KeepOriginal'] = 'True'

        if tmp['KeepSeries']:
            self.keepSeries.SetValue(eval(tmp['KeepSeries']))

        if tmp['SeriesFirst']:
            self.seriesFirst.SetValue(eval(tmp['SeriesFirst']))

        if tmp['KeepOriginal']:
            self.keepOriginal.SetValue(eval(tmp['KeepOriginal']))

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.keepSeries = wx.CheckBox(
            self, -1,
            'Automatically include SeriesDescription'
        )

        # Vertical spacing
        vbox.Add((30, 40), 0, wx.ALL | 30)
        vbox.Add(self.keepSeries, 0, wx.ALIGN_LEFT | wx.ALL | 15)

        self.seriesFirst = wx.CheckBox(self, -1, "Series Name First")

        # Vertical spacing
        vbox.Add((30, 20), 0, wx.ALL | 30)
        vbox.Add(self.seriesFirst, 0, wx.ALIGN_LEFT | wx.ALL | 15)

        self.keepOriginal = wx.CheckBox(self, -1, "Keep Original Files")

        vbox.Add((30, 20), 0, wx.ALL | 30)
        vbox.Add(self.keepOriginal, 0, wx.ALIGN_LEFT | wx.ALL | 15)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.store = wx.Button(self, -1, "Set as Default", size=(120, -1))
        self.revert = wx.Button(self, -1, "Revert to Default", size=(120, -1))
        self.Bind(wx.EVT_BUTTON, self.RevertState, self.revert)
        self.Bind(wx.EVT_BUTTON, self.SaveState, self.store)

        hbox.Add(self.store, 0, wx.ALL, 5)
        hbox.Add(self.revert, 0, wx.ALL, 5)

        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 25)

        self.SetSizer(vbox)


class FileNamePanel(PreferencePanel):

    def __init__(self, parent, config):
        PreferencePanel.__init__(self, parent, 'FilenameFormat',
                                 'Filename Format', config)

        self.create()

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        boxChoices = [
            'Image (0001)',
            'Keep Original Filename',
            'Custom Filename Format:'
        ]

        self.radioBox = wx.RadioBox(self, -1,
                                    style=wx.VERTICAL | wx.BORDER_NONE,
                                    choices=boxChoices)

        self.Bind(wx.EVT_RADIOBOX, self.OnChange, self.radioBox)

        vbox.Add(self.radioBox, 0, wx.TOP | wx.LEFT, 15)

        self.custom = wx.TextCtrl(self, -1, '',
                                  size=(300, -1))
        vbox.Add(self.custom, 0, wx.ALIGN_BOTTOM | wx.LEFT, 50)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.store = wx.Button(self, -1, "Set as Default", size=(120, -1))
        self.revert = wx.Button(self, -1, "Revert to Default", size=(120, -1))
        self.Bind(wx.EVT_BUTTON, self.RevertState, self.revert)
        self.Bind(wx.EVT_BUTTON, self.SaveState, self.store)

        hbox.Add(self.store, 0, wx.ALL, 5)
        hbox.Add(self.revert, 0, wx.ALL, 5)

        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 25)

        self.SetSizer(vbox)

    def RevertState(self, *evnt):
        super(FileNamePanel, self).RevertState()
        savedConfig = configobj.ConfigObj(self.config.filename)
        self.UpdateFromConfig(savedConfig)

    def OnChange(self, *evnt):
        index = self.radioBox.GetSelection()

        # TODO: Make this more robust in the future
        if index != 2:
            self.custom.Disable()
        else:
            self.custom.Enable()

    def UpdateFromConfig(self, config):

        config.interpolation = False

        data = config[self.shortname]

        if 'Selection' in data:
            self.radioBox.SetSelection(int(data['Selection']))
        else:
            self.radioBox.SetSelection(0)

        self.custom.SetValue(data['FilenameString'])

        self.OnChange()

    def GetState(self):
        return {
            'FilenameString': self.custom.GetValue(),
            'Selection': self.radioBox.GetSelection()
        }


class PreferenceDlg(wx.Dialog):

    def __init__(self, *args, **kwargs):
        if 'config' in kwargs:
            self.config = kwargs.pop('config')
        else:
            self.config = configobj.ConfigObj(config.configuration_file)

        wx.Dialog.__init__(self, *args, **kwargs)

        # We want to make this a dict instead of list
        self.pages = dict()
        self.create()

        # Initialize from Config on Create
        self.UpdateFromConfig(self.config)

    def UpdateFromConfig(self, config=None):
        if config is None:
            config = self.config

        [val.UpdateFromConfig(config) for val in self.pages.values()]

    def Show(self, *args):
        # Call superclass constructor
        wx.Dialog.Show(self, *args)

    def create(self):
        self.nb = wx.Notebook(self)
        self.AddModule(AnonymousPanel)
        self.AddModule(FileNamePanel)
        self.AddModule(MiscPanel)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.nb, 1, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.cancel = wx.Button(self, -1, 'Cancel')
        self.apply = wx.Button(self, -1, 'Apply')

        self.cancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        self.apply.Bind(wx.EVT_BUTTON, self.OnApply)

        hbox.Add(self.cancel, 0, wx.ALIGN_RIGHT, 10)
        hbox.Add(self.apply, 0, wx.ALIGN_RIGHT | wx.LEFT, 10)

        vbox.Add(hbox, 0, wx.ALIGN_RIGHT | wx.TOP, 5)
        vbox.Add((10, 10), 0, wx.ALL | 30)

        self.SetSizer(vbox)

    def AddModule(self, panel):
        newPage = panel(self.nb, self.config)

        self.pages[newPage.shortname] = newPage
        self.nb.AddPage(newPage, newPage.title)

    def OnApply(self, *evnt):
        [val.StoreState() for val in self.pages.values()]

        # For now don't write this to the file because it's a local default
        self.Close()
        return self.config

    def OnCancel(self, *evnt):
        # Return configobj that we came in with
        self.Close()
        self.UpdateFromConfig(self.config)
        return self.config

    def ShowModal(self, *args):
        wx.Dialog.ShowModal(self, *args)
        return self.config


class AnonymousPanel(PreferencePanel):

    def __init__(self, parent, config):
        super(AnonymousPanel, self).__init__(parent, 'Anonymization',
                                             'Anonymizing Fields', config)

        self.create()

    def GetState(self):
        # Get all fields that are stored in config but not present in current
        defFields = self.config[self.shortname]['Fields']

        fields = list()
        # Keep only the empty ones
        for i, val in enumerate(self.anonList.FindStrings(defFields)):
            if val is None:
                fields.append(six.ensure_text(defFields[i]))

        # Add to this list the newly checked ones
        fields.extend(self.anonList.GetCheckedStrings(0))

        dat = {'Fields': fields,
               'Replacements': self.anonList.GetReplacementDict()}

        return dat

    def RevertState(self, *evnt):
        # Update self.config
        super(AnonymousPanel, self).RevertState()
        savedConfig = configobj.ConfigObj(self.config.filename)
        savedConfig.interpolation = False
        self.UpdateFromConfig(savedConfig)

    def SetDicomFields(self, values):
        self.anonList.SetStringItems(values)
        self.UpdateFromConfig(self.config)

    def UpdateFromConfig(self, config):
        data = config[self.shortname]

        # The fields that we care about are "Fields" and "Replacements"
        fields = data['Fields']
        self.anonList.UnCheckAll()
        self.anonList.CheckStrings(fields, col=0)
        self.anonList.ClearColumn(1)

        # Now put in substitutes
        self.anonList.SetReplacementDict(data['Replacements'])

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self, -1, "Fields to Omit")
        vbox.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 10)

        self.anonList = AnonymizeList(self)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.store = wx.Button(self, -1, "Set as Default", size=(120, -1))
        self.revert = wx.Button(self, -1, "Revert to Defaults", size=(120, -1))
        self.revert.Bind(wx.EVT_BUTTON, self.RevertState)
        self.store.Bind(wx.EVT_BUTTON, self.SaveState)

        opts = wx.ALIGN_RIGHT | wx.TOP | wx.LEFT

        hbox.Add(self.store, 0, opts, 10)
        hbox.Add(self.revert, 0, opts, 10)

        vbox.Add(self.anonList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        self.SetSizer(vbox)
