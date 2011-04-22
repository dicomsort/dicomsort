import wx
import gui
import wx.py
import configobj

class PreferencePanel(wx.Panel):

    def __init__(self,parent,shortname,title,config):
        wx.Panel.__init__(self,parent,-1)
        self.shortname = shortname
        self.config = config
        self.title = title

    def GetState(self):
        raise TypeError('Abstract Method!')

    def SaveState(self,*evnt):
        # Load since last saved version
        tmpconfig = configobj.ConfigObj(self.config.filename)
        self.StoreState(config=tmpconfig)

        # Write just the change from this panel
        tmpconfig.write()

    def UpdateFromConfig(self,config=None):
        raise TypeError('Abstract Method!')

    def RevertState(self,*evnt):
        # Load a temporary copy
        tmpconfig = configobj.ConfigObj(self.config.filename)
        self.config[self.shortname] = tmpconfig[self.shortname]
        # TODO: See if all of these configobjs need to be closed()

    def StoreState(self, config=None):
        if config == None:
            config = self.config

        config[self.shortname] = self.GetState()


    def UpdateFromConfig(self,config=None):
        raise TypeError('Abstract Method!')


        config[self.shortname] = self.GetState()

import anonymizer

class FileNamePanel(PreferencePanel):

    def __init__(self,parent,config):
        PreferencePanel.__init__(self,parent,'FilenameFormat',
                                            'Filename Format',config)

        self.create()

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        boxChoices = ['Image (0001)',
                      'Keep Original Filename',
                      'Custom Filename Format:']

        self.radioBox = wx.RadioBox(self,-1,
                style=wx.VERTICAL | wx.RB_USE_CHECKBOX | wx.BORDER_NONE ,
                choices=boxChoices)

        self.Bind(wx.EVT_RADIOBOX,self.OnChange,self.radioBox)

        vbox.Add(self.radioBox,0,wx.TOP | wx.LEFT, 15)

        self.custom = wx.TextCtrl(self,-1,'',
                            size=(300,-1))
        vbox.Add(self.custom,0,wx.ALIGN_BOTTOM | wx.LEFT,50)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.store = wx.Button(self,-1,"Set as Default", size=(120,-1))
        self.revert = wx.Button(self,-1,"Revert to Default",size=(120,-1))
        self.Bind(wx.EVT_BUTTON,self.RevertState,self.revert)
        self.Bind(wx.EVT_BUTTON,self.SaveState,self.store)

        hbox.Add(self.store,0,wx.ALL,5)
        hbox.Add(self.revert,0, wx.ALL, 5)

        vbox.Add(hbox,0,wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 25)

        self.SetSizer(vbox)

    def RevertState(self,*evnt):
        super(FileNamePanel,self).RevertState()
        savedConfig = configobj.ConfigObj(self.config.filename)
        self.UpdateFromConfig(savedConfig)

    def OnChange(self,*evnt):
        index = self.radioBox.GetSelection()

        #TODO: Make this more robust in the future
        if index != 2:
            self.custom.Disable()
        else:
            self.custom.Enable()

    def UpdateFromConfig(self,config):

        config.interpolation = False

        data = config[self.shortname]

        if data.has_key('Selection'):
            self.radioBox.SetSelection(int(data['Selection']))
        else:
            self.radioBox.SetSelection(0)

        self.custom.SetValue(data['FilenameString'])

        self.OnChange()

    def GetState(self):
        d = {'FilenameString':self.custom.GetValue(),
             'Selection':self.radioBox.GetSelection()}

        return d

class PreferenceDlg(wx.Dialog):

    def __init__(self,*args,**kwargs):
        if kwargs.has_key('config'):
            self.config = kwargs.pop('config')
        else:
            self.config = configobj.ConfigObj('dicomSort.ini')

        wx.Dialog.__init__(self,*args,**kwargs)

        # We want to make this a dict instead of list
        self.pages = dict() 
        self.create()

        # Initialize from Config on Create
        self.UpdateFromConfig(self.config)

    def UpdateFromConfig(self,config=None):
        if config == None:
            config = self.config

        [val.UpdateFromConfig(config) for key,val in self.pages.items()]

    def Show(self,*args):
        # Call superclass constructor
        wx.Dialog.Show(self,*args)

    def create(self):
        self.nb = wx.Notebook(self)
        self.AddModule(anonymizer.AnonymousPanel)
        self.AddModule(FileNamePanel)

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.nb, 1, wx.EXPAND)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.cancel = wx.Button(self,-1,'Cancel')
        self.apply = wx.Button(self,-1,'Apply')

        self.cancel.Bind(wx.EVT_BUTTON,self.OnCancel)
        self.apply.Bind(wx.EVT_BUTTON,self.OnApply)

        hbox.Add(self.cancel,0,wx.ALIGN_RIGHT, 10)
        hbox.Add(self.apply,0,wx.ALIGN_RIGHT | wx.LEFT, 10)

        vbox.Add(hbox,0,wx.ALIGN_RIGHT | wx.TOP, 5)
        self.SetSizer(vbox)

    def AddModule(self,panel):
        newPage = panel(self.nb,self.config)

        self.pages[newPage.shortname] = newPage
        self.nb.AddPage(newPage,newPage.title)

    def OnApply(self,*evnt):
        [val.StoreState() for key,val in self.pages.items()]

        # For now don't write this to the file because it's a local default
        self.Close()
        return self.config

    def OnCancel(self,*evnt):
        # Return configobj that we came in with
        self.Close()
        self.UpdateFromConfig(self.config)
        return self.config


    def ShowModal(self,*args):
        wx.Dialog.ShowModal(self,*args)
        return self.config


if __name__ == "__main__":
    app = gui.DebugApp(0)

    p = PreferenceDlg(None,-1,"DICOM sort preferences",size=(400,500),pos=(708,0))
    p.Show()

    anonList = p.pages['Anonymization']

    app.SetTopWindow(p)

    app.MainLoop()
