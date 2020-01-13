import wx

from dicomsort.gui import widgets


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


class AnonymizeList(widgets.CheckListCtrl):

    def __init__(self, *args, **kwargs):
        super(AnonymizeList, self).__init__(*args, **kwargs)

        self.InsertColumn(0, 'DICOM Property', width=200)
        self.InsertColumn(1, 'Replacement Value')

        self.SetColumnEditable(1)

    def GetReplacementDict(self):
        res = dict()

        x = [i for i in range(self.ItemCount) if len(self.GetStringItem(i, 1))]

        for row in x:
            res[self.GetStringItem(row, 0)] = self.GetStringItem(row, 1)

        return res

    def GetAnonDict(self):

        anonDict = dict()

        for key, val in self.GetCheckedStrings():
            anonDict[key] = val

        return anonDict

    def SetReplacementDict(self, dictionary):
        keys = list(dictionary.keys())
        inds = self.FindStrings(keys, 0)

        for i, row in enumerate(inds):
            if row is None:
                continue

            self.SetItem(row, 1, dictionary[keys[i]])

    def CheckStrings(self, strings, col=0):
        inds = [ind for ind in self.FindStrings(strings, col)
                if ind is not None]
        self.CheckItems(inds)

    def GetDicomField(self, row):
        return self.GetItem(row, 0).Text
