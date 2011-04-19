import wx
import anonymize
import wx.py
import configobj

class PreferenceDlg(wx.Dialog):

    def __init__(self,*args,**kwargs):
        if kwargs.has_key('config'):
            self.config = kwargs.pop('config')
        else:
            self.config = configobj.ConfigObj('dicomSort.ini')

        wx.Dialog.__init__(self,*args,**kwargs)

        self.pages = []

        self.create()

    def create(self):
        self.nb = wx.Notebook(self)
        self.add_module(AnonymousPanel,'Anonymized Fields')
        self.add_module(FileNamePanel,'Filename Format')

        self.Bind(wx.EVT_CLOSE, self.close)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.nb, 1, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.cancel = wx.Button(self,-1,'Cancel')
        self.ok = wx.Button(self,-1,'Apply')

        hbox.Add(self.cancel,0,wx.ALIGN_RIGHT, 10)
        hbox.Add(self.ok,0,wx.ALIGN_RIGHT | wx.LEFT, 10)

        vbox.Add(hbox,0,wx.ALIGN_RIGHT | wx.TOP, 5)
        self.SetSizer(vbox)

    def add_module(self,panel,title):
        self.pages.append(panel(self.nb,self.config))
        self.nb.AddPage(self.pages[-1],title)

    def close(self,*evnt):
        [page.apply() for page in self.pages]

        # return the config object PRIOR to saving to file
        return self.config

    def apply(self,*evnt):
        # Actually write the config to file
        self.close().write()

class PreferencePanel(wx.Panel):

    def __init__(self,parent,shortname,config):
        wx.Panel.__init__(self,parent,-1)
        self.shortname = shortname
        self.config = config

    def GetState(self):
        raise TypeError('Abstract Method!')

    def apply(self,*evnt):
        self.config[self.shortname] = self.GetState()

class FileNamePanel(PreferencePanel):

    def __init__(self,parent,config):
        PreferencePanel.__init__(self,parent,'FilenameFormat',config)

    def GetState(self):
        #TODO: Actually make this point to a value
        return {'FilenameString':'%(ImageType)s (%(InstanceNumber)04d)'}

class AnonymousPanel(PreferencePanel):

    def __init__(self,parent,config):
        PreferencePanel.__init__(self,parent,'Anonymization',config)

        self.create()

    def GetState(self):
        dat =  {'Fields':self.anonList.GetCheckedStrings(0),
                'Replacements':self.anonList.GetReplacements()}
        return dat

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self,-1,"Fields to Omit")
        vbox.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 10)

        self.anonList = anonymize.AnonymizeList(self)

        #self.anonList.SetChoices([(0,'peanut','butter'),(1,'and','jelly')])
        self.anonList.SetStringItems([('Peanut','Butter'),('and','jelly')])

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.store = wx.Button(self, -1, "Set as Default", size=(120,-1))
        self.revert = wx.Button(self, -1, "Revert to Defaults",size=(120,-1))
        #self.revert.Bind(wx.EVT_BUTTON, self.anonList.reset_to_defaults)

        opts = wx.ALIGN_RIGHT | wx.TOP | wx.LEFT

        hbox.Add(self.store, 0, opts, 10)
        hbox.Add(self.revert, 0, opts, 10)

        vbox.Add(self.anonList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        self.SetSizer(vbox)


app = wx.App(0)

debug = wx.Frame(None,-1,'DEBUGGER',size=(700,500),pos=(0,0))
crust = wx.py.crust.Crust(debug)
debug.Show()

p = PreferenceDlg(None,-1,"DICOM sort preferences",size=(400,500),pos=(708,0))
p.Show()

anonList = p.pages[0].anonList

conf = wx.Config()

app.SetTopWindow(p)

app.MainLoop()


