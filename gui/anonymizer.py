import configobj
import wx
import platform
from gui import widgets

class QuickRenameDlg(wx.Dialog):

    def __init__(self,*args,**kwargs):
        tmp =kwargs.pop('anonList')
        wx.Dialog.__init__(self,*args,**kwargs)
        self.anonList = tmp;
        self.values = dict()
        
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.values = self.anonList.GetReplacementDict()
        if self.values.has_key('PatientsName'):
            initial = self.values['PatientsName']
        else:
            initial = ''

        vbox.Add(wx.StaticText(self,-1,'Patient Name'),0,wx.TOP | wx.ALIGN_CENTER,15)
        self.patientName = wx.TextCtrl(self,-1,initial,size=(200,20),
                                style=wx.TE_PROCESS_ENTER)

        self.Bind(wx.EVT_TEXT_ENTER,self.OnAccept,self.patientName)

        vbox.Add(self.patientName,0,wx.TOP | wx.ALIGN_CENTER, 5)

        self.samecheck = wx.CheckBox(self,-1,'Use as Patient ID')
        self.samecheck.SetValue(True)

        vbox.Add(self.samecheck,0,wx.TOP | wx.ALIGN_CENTER, 10)

        self.btnOK = wx.Button(self,-1,'Ok')
        self.btnOK.Bind(wx.EVT_BUTTON,self.OnAccept)

        vbox.Add(self.btnOK,0,wx.TOP | wx.ALIGN_CENTER, 15)

        self.SetSizer(vbox)

        self.patientName.SetFocus()

    def GetValues(self):
        res = dict()
        res['PatientsName'] = self.patientName.GetValue()
        
        if self.samecheck.IsChecked():
            res['PatientID'] = '%(PatientsName)s'
        
        return res

    def OnAccept(self,*evnt):
        oldDict = self.anonList.GetReplacementDict()
        oldDict.update(self.GetValues())
        self.anonList.SetReplacementDict(oldDict)
        self.Close()

class AnonymizeListXP(widgets.CheckListCtrlXP):

    def __init__(self,*args,**kwargs):
        super(AnonymizeListXP,self).__init__(*args,**kwargs)

        self.SetColumnEditable(2)

    def GetReplacementDict(self):
        res = dict()

        x = [i for i in range(self.GetNumberRows()) if len(self.GetStringItem(i,2))]

        for row in x:
            res[self.GetStringItem(row,1)] = self.GetStringItem(row,2)

        return res

    def GetAnonDict(self):
        anonDict = dict()

        for key,val in self.GetCheckedStrings():
            anonDict[key] = val

        return anonDict

    def SetReplacementDict(self,dictionary):
        keys = dictionary.keys()
        inds = self.FindStrings(keys,1)

        for i,row in enumerate(inds):
            if row == None:
                continue

            self.GetTable().SetValue(row,2,dictionary[keys[i]])

    def CheckStrings(self,strings,col=1):
        inds = [ind for ind in self.FindStrings(strings,col) if ind != None]
        self.CheckItems(inds)

    def GetDicomField(self,row):
        return self.GetTable().GetValue(row,1)

class AnonymizeList(widgets.CheckListCtrl):

    def __init__(self,*args,**kwargs):
        super(AnonymizeList,self).__init__(*args,**kwargs)

        self.InsertColumn(0,'DICOM Property',width=200)
        self.InsertColumn(1,'Replacement Value')

        self.SetColumnEditable(1)

    def GetReplacementDict(self):
        res = dict()

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

import preferences

class AnonymousPanel(preferences.PreferencePanel):

    def __init__(self,parent,config):
        super(AnonymousPanel,self).__init__(parent,'Anonymization',
                                            'Anonymizing Fields',config)

        self.create()

    def GetState(self):
        if platform.win32_ver()[0] == 'XP':
            index = 1;
        else:
            index = 0;
        
        # Get all fields that are stored in config but not present in current
        defFields = self.config[self.shortname]['Fields']

        fields = list()
        # Keep only the empty ones
        for i,val in enumerate(self.anonList.FindStrings(defFields)):
                if val == None:
                    fields.append(unicode(defFields[i]))

        # Add to this list the newly checked ones
        fields.extend(self.anonList.GetCheckedStrings(index))

        dat = {'Fields':fields,
               'Replacements':self.anonList.GetReplacementDict()}

        return dat

    def RevertState(self,*evnt):
        # Update self.config
        super(AnonymousPanel,self).RevertState()
        savedConfig = configobj.ConfigObj(self.config.filename)
        savedConfig.interpolation = False
        self.UpdateFromConfig(savedConfig)

    def SetDicomFields(self,values):
        self.anonList.SetStringItems(values)
        self.UpdateFromConfig(self.config)

    def UpdateFromConfig(self,config):
        data = config[self.shortname]

        # The fields that we care about are "Fields" and "Replacements"
        fields = data['Fields']
        self.anonList.UnCheckAll()
        if platform.win32_ver()[0] == 'XP':
            self.anonList.CheckStrings(fields,col=1)
            self.anonList.ClearColumn(2)
            self.anonList.SetColumnSizes([20,175,155])
        else:
            self.anonList.CheckStrings(fields,col=0)
            self.anonList.ClearColumn(1)

        # Now put in substitutes
        self.anonList.SetReplacementDict(data['Replacements'])

    def create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        title = wx.StaticText(self,-1,"Fields to Omit")
        vbox.Add(title, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP | wx.BOTTOM, 10)

        if platform.win32_ver()[0] == 'XP':
            self.anonList = AnonymizeListXP(self)
        else:
            self.anonList = AnonymizeList(self)

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
