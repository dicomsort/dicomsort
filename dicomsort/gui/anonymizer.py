from dicomsort.gui import widgets


class AnonymizeList(widgets.CheckListCtrl):

    def __init__(self, *args, **kwargs):
        super(AnonymizeList, self).__init__(*args, **kwargs)

        self.InsertColumn(0, 'DICOM Property', width=200)
        self.InsertColumn(1, 'Replacement Value', width=-1)

        self.SetColumnEditable(1)

    def GetReplacementDict(self):
        res = dict()

        x = [i for i in range(self.ItemCount) if len(self.GetStringItem(i, 1))]

        for row in x:
            res[self.GetStringItem(row, 0)] = self.GetStringItem(row, 1)

        return res

    def GetAnonDict(self):
        return {k: v for k, v in self.GetCheckedStrings()}

    def SetReplacementDict(self, dictionary):
        keys = list(dictionary.keys())
        indices = self.FindStrings(keys, 0)

        for i, row in enumerate(indices):
            if row is None:
                continue

            self.SetItem(row, 1, dictionary[keys[i]])

    def CheckStrings(self, strings, col=0):
        for index in self.FindStrings(strings, col):
            if index is None:
                continue

            self.CheckItem(index)

    def GetDicomField(self, row):
        return self.GetItem(row, 0).Text
