import wx
import gui
import preferences 

class AnonymizeList(gui.CheckListCtrl):

    def __init__(self,*args,**kwargs):
        gui.CheckListCtrl.__init__(self,*args,**kwargs)

        self.InsertColumn(0,'DICOM Property',width=200)
        self.InsertColumn(1,'Replacement Value')

        self.SetColumnEditable(1)

    def GetReplacementDict(self):
        res = dict()

        ilist = self.GetItemList(1)

        x = [i for i in range(self.ItemCount) if len(self.GetStringItem(i,1))]

        for row in x:
            res[self.GetStringItem(row,0)] = self.GetStringItem(row,1)

        return res

    def GetAnonDict(self):

        anonDict = dict()

        for key,val in self.GetCheckedStrings():
            anonDict[key] = val

        return anonDict

    def SetReplacementDict(self,dictionary):
        keys = dictionary.keys()
        inds = self.FindStrings(keys,0)

        for i,row in enumerate(inds):
            if row == None:
                continue

            self.SetStringItem(row,1,dictionary[keys[i]])

    def CheckStrings(self,strings,col=0):
        inds = [ind for ind in self.FindStrings(strings,col) if ind != None]
        self.CheckItems(inds)

    def GetDicomField(self,row):
        return self.GetItem(row,0).Text

    #def GetAnonymousFields(self):
    #    return [self.GetDicomField(i) for i in self.GetAnonymousIndex()]

class AnonymousPanel(preferences.PreferencePanel):

    def __init__(self,parent,config):
        preferences.PreferencePanel.__init__(self,parent,'Anonymization',config)

        self.create()

    def GetState(self):
        dat =  {'Fields':self.anonList.GetCheckedStrings(0),
                'Replacements':self.anonList.GetReplacements()}
        return dat

    def RevertState(self,*evnt):
        # Update self.config
        PreferencePanel.RevertState(self)
        savedConfig = configobj.ConfigObj(self.config.filename)
        self.UpdateFromConfig(savedConfig)

    def SetDicomFields(self,values):
        self.anonList.SetStringItems(values)
        self.UpdateFromConfig(self.config)

    def UpdateFromConfig(self,config):
        data = config[self.shortname]

        # The fields that we care about are "Fields" and "Replacements"
        fields = data['Fields']
        self.anonList.UnCheckAll()
        self.anonList.CheckStrings(fields,col=0)

        # Now put in substitutes
        self.anonList.ClearColumn(1)
        self.anonList.SetReplacements(data['Replacements'])

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self,-1,"Fields to Omit")
        vbox.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 10)

        self.anonList = AnonymizeList(self)

        #self.anonList.SetChoices([(0,'peanut','butter'),(1,'and','jelly')])
        self.anonList.SetStringItems([('Peanut','Butter'),('and','jelly')])

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.store = wx.Button(self, -1, "Set as Default", size=(120,-1))
        self.revert = wx.Button(self, -1, "Revert to Defaults",size=(120,-1))
        self.revert.Bind(wx.EVT_BUTTON, self.RevertState)
        self.store.Bind(wx.EVT_BUTTON, self.SaveState)

        opts = wx.ALIGN_RIGHT | wx.TOP | wx.LEFT

        hbox.Add(self.store, 0, opts, 10)
        hbox.Add(self.revert, 0, opts, 10)

        vbox.Add(self.anonList, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        vbox.Add(hbox, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 15)
        self.SetSizer(vbox)

