import os
import configobj
import dicomsorter
import sys
import wx
import wx.lib.newevent
import wx.py
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from wx.lib.mixins.listctrl import CheckListCtrlMixin,TextEditMixin
configFile = 'dicomSort.ini'

defaultConfig = {'Anonymization':
                    {'Fields':['OtherPatientsIDS',
                               'PatientID',
                               'PatientsBirthDate',
                               'PatientsName',
                               'ReferringPhysiciansName',
                               'RequestingPhysician'],
                     'Replacements':
                        {'PatientsName':'ANONYMOUS'}},
                 'FilenameFormat':
                    {'FilenameString':'%(ImageType)s (%(InstanceNumber)04d)'}}

# Define even
PathEvent,EVT_PATH = wx.lib.newevent.NewEvent()
PopulateEvent,EVT_POPULATE_FIELDS = wx.lib.newevent.NewEvent()

def ThrowError(message,titl = 'Error'):
    """
    Generic way to throw an error and display the appropriate dialog
    """
    dlg = wx.MessageDialog(None,message,title,wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

class CheckListCtrl(wx.ListCtrl,ListCtrlAutoWidthMixin,
        CheckListCtrlMixin,TextEditMixin):

    def __init__(self,parent):
        wx.ListCtrl.__init__(self,parent,-1,style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)

        # The order here matter because we favor Check over Edit
        TextEditMixin.__init__(self)
        CheckListCtrlMixin.__init__(self)

        self.editColumns = []

    def _GetCheckedIndexes(self):
        return [i for i in range(self.ItemCount) if self.IsChecked(i)]

    def ClearColumn(self,col):
        [self.SetStringItem(i,col,'') for i in range(self.ItemCount)]

    def SetColumnEditable(self,column,edit=True):
        if edit:
            if column not in self.editColumns:
                self.editColumns.append(column)
        else:
            if column in self.editColumns:
                self.editColumns.remove(column)

    def SetStringItems(self,items):
        self.DeleteAllItems()

        for item in items:
            if isinstance(item,str):
                item = [item,]

            row = self.InsertStringItem(sys.maxint,item[0])

            for col in range(1,len(item)):
                self.SetStringItem(row,col,item[col])

    def CheckItems(self,itemIndex):
        [self.CheckItem(index) for index in itemIndex]

    def GetCheckedItems(self,col=None):
        return [self.GetItemList(r,col) for r in self._GetCheckedIndexes()]

    def UnCheckAll(self):
        [self.CheckItem(index,False) for index in range(self.ItemCount)]

    def GetCheckedStrings(self,col=None):
        return [self.GetStringItem(r,col) for r in self._GetCheckedIndexes()]

    def FindStrings(self,strings,col=0):
        strings = [unicode(string) for string in strings]

        fields = [item.Text for item in self.GetItemList(col)]

        inds = list()

        for string in strings:
            try:
                inds.append(fields.index(unicode(string)))
            except ValueError:
                inds.append(None)

        return inds

    def GetItemList(self,column = None):
        if column == None:
            return [self.GetItemList(c) for c in range(self.ColumnCount)]
        else:
            return [self.GetItem(r,column) for r in range(self.ItemCount)]

    def GetStringItem(self,row,column=None):
        if column == None:
            return [self.GetStringItem(row,c) for c in range(self.ColumnCount)]
        else:
            return self.GetItem(row,column).Text

    def OpenEditor(self,column,row):
        """
        Overloaded method to render certain columns un-editable
        """
        if column not in self.editColumns:
            return
        else:
            # Call superclass edit method
            TextEditMixin.OpenEditor(self,column,row)

class PathEditCtrl(wx.Panel):
    def __init__(self,*args,**kwargs):
        wx.Panel.__init__(self,*args,**kwargs)
        self._initialize_controls()
        self.path = ''
        self.Bind(wx.EVT_TEXT_ENTER,self.ValidatePath,self.edit)

    def ValidatePath(self,*evnt):
        path = os.path.abspath(self.edit.GetValue())

        # update the box with the absolute path
        self.edit.SetValue(path)

        if os.path.isdir(path):
            self.path = path
            self.Notify()
        else:
            errorMsg = 'The Directory %(a)s does not exist!' % {'a':path}
            throw_error(errorMsg,'Invalid Location')

    def _initialize_controls(self):
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        opts = wx.ALIGN_CENTER_VERTICAL | wx.LEFT | wx.RIGHT | wx.TOP

        self.edit = wx.TextCtrl(self,-1,"",style=wx.TE_PROCESS_ENTER)
        hbox.Add(self.edit, 1, opts, 5)

        self.browse = wx.Button(self,-1,label="Browse")
        hbox.Add(self.browse, 0, opts, 10)

        self.browse.Bind(wx.EVT_BUTTON, self.BrowsePaths)

        self.SetSizer(hbox)

    def Notify(self,*evnt):
        global PathEvent
        event = PathEvent(path=self.path)
        wx.PostEvent(self,event)

    def BrowsePaths(self,*evnt):
        # Open the dialog and search
        path = wx.DirDialog(self.GetParent(),"Please Select Directory",
                                    defaultPath=self.path)
        path.CenterOnParent()

        if path.ShowModal() == wx.ID_OK:
            self.edit.SetValue(path.GetPath())
            self.ValidatePath()

        path.Destroy()

class FieldSelector(wx.Panel):

    def __init__(self,parent,id=-1,size=(250,300),choices=[],titles=['','']):
        wx.Panel.__init__(self,parent,id=id,size=size)

        self.choices = choices
        self.titles = titles

        self._initialize_controls()

    def Filter(self,string=None):
        if string and isinstance(string,str):
            self.search.SetValue(string)
        else:
            string = self.search.GetValue()

        newVals = [p for p in self.choices if re.search(string,p,re.IGNORECASE)]

        self.options.SetItems(newVals)

    def _return_focus(self):
        return

    def _initialize_controls(self):

        self.titleL        = wx.StaticText(self,-1,self.titles[0])
        self.options    = wx.ListBox(self,-1,choices=self.choices)

        self.search        = wx.SearchCtrl(self,-1,"",style=wx.TE_PROCESS_ENTER)

        self.titleR        = wx.StaticText(self,-1,self.titles[1])
        self.selected    = wx.ListBox(self,-1,choices=[])

        # Setup double-click callbacks
        self.options.Bind(wx.EVT_LISTBOX_DCLICK, self.SelectItem)
        self.selected.Bind(wx.EVT_LISTBOX_DCLICK, self.DeselectItem)

        # Setup Search Control
        self.search.Bind(wx.EVT_TEXT, self.Filter)
        self.search.Bind(wx.EVT_TEXT_ENTER, self._return_focus)

        # Setup controls:
        self.bAdd = wx.Button(self,-1,label=">>")
        self.bRemove = wx.Button(self,-1,label="<<")
        self.bUp = wx.Button(self,-1,label="Up")
        self.bDown = wx.Button(self,-1,label="Down")

        self.bAdd.Bind(wx.EVT_BUTTON, self.SelectItem)
        self.bRemove.Bind(wx.EVT_BUTTON, self.DeselectItem)
        self.bUp.Bind(wx.EVT_BUTTON, self.PromoteSelection)
        self.bDown.Bind(wx.EVT_BUTTON, self.DemoteSelection)

        self._initialize_layout()

    def _initialize_layout(self):
        # BoxSizer containing the options to select
        vboxOptions = wx.BoxSizer(wx.VERTICAL)

        vboxOptions.Add(self.titleL, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vboxOptions.Add(self.options, 1, 
                        wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vboxOptions.Add(self.search, 0, 
                        wx.ALIGN_CENTER_HORIZONTAL | wx.EXPAND | wx.ALL, 10)

        # BoxSizer containing the selected options
        vboxSelect = wx.BoxSizer(wx.VERTICAL)

        vboxSelect.Add(self.titleR, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vboxSelect.Add(self.selected, 1,
                        wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

        # BoxSizer housing the controls
        vboxControl = wx.BoxSizer(wx.VERTICAL)

        vboxControl.Add(self.bAdd,0,wx.ALIGN_CENTER_HORIZONTAL|wx.TOP,30)
        vboxControl.Add(self.bRemove,0,wx.ALIGN_CENTER_HORIZONTAL|wx.TOP,15)
        vboxControl.Add(self.bUp,0,wx.ALIGN_CENTER_HORIZONTAL|wx.TOP,15)
        vboxControl.Add(self.bDown,0,wx.ALIGN_CENTER_HORIZONTAL|wx.TOP,15)

        # Horizontal Box that contains all elements
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        
        hbox.Add(vboxOptions,1,wx.EXPAND | wx.ALL, 10)
        hbox.Add(vboxControl,0,wx.ALL,10)
        hbox.Add(vboxSelect,1,wx.EXPAND | wx.ALL, 10)

        self.SetSizer(hbox)

    def PromoteSelection(self,*evnt):
        self._move_selection(-1)

    def DemoteSelection(self,*evnt):
        self._move_selection(1)

    def _move_selection(self,inc):
        """
        Shared method for moving an item around the list.
        There really has to be a better way...
        """

        index = self.selected.GetSelection()

        if inc < 0 and (self.selected.Count == 1 or index == 0):
            return
        elif (inc > 0 and index == self.selected.Count-1):
            return

        prop = self.selected.GetStringSelection()

        self.selected.Delete(index)
        self.selected.Insert(prop,index + inc)
        self.selected.Select(index + inc)

    def SelectItem(self,*evnt):
        item = self.options.GetStringSelection()
        self.selected.Append(item)

    def DeselectItem(self,*evnt):
        index = self.selected.GetSelection()
        self.selected.Delete(index)

        self.selected.Select(index-1)

    def SetTitles(self,titleL,titleR):
        self.leftBox

    def SetOptions(self,optionList=[]):
        # clear
        self.options.SetItems(optionList)
        self.choices = optionList

        # TODO: Future checks to make sure that fields are in this
        
class DicomSort(wx.App):

    def __init__(self,*args):
        wx.App.__init__(self,*args)
        self.frame = MainFrame(None,-1,"DicomSort",size=(500,500))
        self.frame.Show()

    def MainLoop(self,*args):
        wx.App.MainLoop(self,*args)

class DebugApp(DicomSort):
    """
    Develops the debugging framework for easy testing etc.
    """

    def __init__(self,*args):
        super(DebugApp,self).__init__(*args)

        pos = (self.frame.Position[0] + self.frame.Size[0],self.frame.Position[1])

        self.debug = wx.Frame(None,-1,'DEBUGGER',size=(700,500),pos=pos)
        self.crust = wx.py.crust.Crust(self.debug)
        self.debug.Show()

        # Set the correct Main window
        self.SetTopWindow(self.frame)

    def MainLoop(self,*args):
        # Call superclass MainLoop
        super(DebugApp,self).MainLoop(*args)
        self.debug.Destroy()

from gui import preferences

class MainFrame(wx.Frame):

    def __init__(self,*args,**kwargs):
        wx.Frame.__init__(self,*args,**kwargs)
        self._initialize_components()
        self._initialize_menus()

        # Use os.getcwd() for now
        self.dicomSorter = dicomsorter.DicomSorter()

        # Get config from parent
        self.config = configobj.ConfigObj('dicomSort.ini')
        # Set interpolation to false since we use formatted strings
        self.config.interpolation = False

        # Check to see if we need to populate the config file
        if len(self.config.keys()) == 0:
            global defaultConfig
            self.config.update(defaultConfig)
            self.config.write()

        self.prefDlg = preferences.PreferenceDlg(None,-1,"DicomSort Preferences",
                            config = self.config, size=(400,400))

    def _initialize_components(self):
        global DEBUG

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.pathEditor = PathEditCtrl(self,-1)
        vbox.Add(self.pathEditor,0,wx.EXPAND)

        self.selector = FieldSelector(self,titles=['DICOM Properties',
                                                   'Properties to Use'])
        vbox.Add(self.selector,1,wx.EXPAND)

        self.SetSizer(vbox)

        self.pathEditor.Bind(EVT_PATH,self.FillList)

    def Sort(self,*evnt):
        self.anonymize = 0 

        if self.anonymize:
            print 'Retrieving anonymizing dictionary...'
            anonTab = self.prefDlg.pages[0]
            anonDict = anonTab.anonList.GetAnonDict()
            self.dicomSorter.SetAnonRules(anonDict)
        else:
            self.dicomSorter.SetAnonRules(dict())

        # TODO: Get folder format
        dFormat = []

        # TODO: Keep Series
        keepSeries = True

        fFormat = self.config['FilenameFormat']['FilenameString']

        # TODO: Get "keepOriginalFilename"
        original = False

        self.dicomSorter.filename = fFormat
        self.dicomSorter.folders = dFormat
        self.dicomSorter.keep_filename = original
        self.dicomSorter.includeSeries = keepSeries

        outputDir = self.SelectOutputDir()

        if outputDir == None:
            return
        
        self.dicomSorter.Sort(outputDir)

    def SelectOutputDir(self):
        # TODO: Set default path
        dlg = wx.DirDialog(None,"Please select an output directory")

        if dlg.ShowModal() == wx.ID_OK:
            outputDir = dlg.GetPath()
        else:
            outputDir = None

        dlg.Destroy()

        return outputDir

    def OnPreferences(self,*evnt):
        self.config = self.prefDlg.ShowModal()

    def OnQuit(self,*evnt):
        sys.exit()

    def OnAbout(self,*evnt):
        return

    def OnHelp(self,*evnt):
        return

    def _menu_generator(self,parent,name,arguments):
        menu = wx.Menu()

        for item in arguments:
            if item == '----':
                menu.AppendSeparator()
            else:
                menuitem = wx.MenuItem(menu,-1,'\t'.join(item[0:2]))
                if item[2] != '':
                    self.Bind(wx.EVT_MENU,item[2],menuitem)

                menu.AppendItem(menuitem)

        parent.Append(menu,name)

    def _initialize_menus(self):
        menubar = wx.MenuBar()

        file = [['&Open Directory','Ctrl+O',self.pathEditor.BrowsePaths],
                ['&Sort Images','Ctrl+S',self.Sort],
                '----',
                ['&Preferences...','Ctrl+,',self.OnPreferences],
                '----',
                ['&Exit','Ctrl+W',self.OnQuit]]

        self._menu_generator(menubar,'&File',file)

        help = [['About','',self.OnAbout],
                ['&Help','Ctrl+?',self.OnHelp]]

        self._menu_generator(menubar,'&Help',help)

        self.SetMenuBar(menubar)

    def FillList(self,evnt):
        self.dicomSorter.pathname = evnt.path
        try:
            fields = self.dicomSorter.GetAvailableFields()
        except dicomsorter.DicomFolderError:
            errMsg = ''.join([evnt.path,' contains no DICOMs'])
            throw_error(errMsg,'No DICOMs Present')
            return

        self.selector.SetOptions(fields)

        # This is clunky
        # TODO: Change PrefDlg to a dict
        self.prefDlg.pages['Anonymization'].SetDicomFields(fields)

        self.Notify(PopulateEvent,fields=fields)

    def Notify(self,evntType,**kwargs):
        event = evntType(**kwargs)
        wx.PostEvent(self,event)


