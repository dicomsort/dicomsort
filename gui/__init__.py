import os
import configobj
import dicomsorter
import sys
import widgets
import wx
import wx.lib.newevent

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
                    {'FilenameString':'%(ImageType)s (%(InstanceNumber)04d)',
                     'Selection':0}}

# Define even
PathEvent,EVT_PATH = wx.lib.newevent.NewEvent()
PopulateEvent,EVT_POPULATE_FIELDS = wx.lib.newevent.NewEvent()
SortEvent,EVT_SORT = wx.lib.newevent.NewEvent()
CounterEvent,EVT_COUNTER = wx.lib.newevent.NewEvent()

def ThrowError(message,title='Error'):
    """
    Generic way to throw an error and display the appropriate dialog
    """
    dlg = wx.MessageDialog(None,message,title,wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()


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
        self.Create()
        self._InitializeMenus()

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

        self.Bind(wx.EVT_CLOSE,self.OnQuit)

        self.CreateStatusBar()
        self.SetStatusText("Ready...")

    def Create(self):
        global DEBUG

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.pathEditor = widgets.PathEditCtrl(self,-1)
        vbox.Add(self.pathEditor,0,wx.EXPAND)

        self.selector = widgets.FieldSelector(self,titles=['DICOM Properties',
                                                   'Properties to Use'])

        self.selector.Bind(EVT_SORT,self.Sort)

        vbox.Add(self.selector,1,wx.EXPAND)

        self.SetSizer(vbox)

        self.pathEditor.Bind(EVT_PATH,self.FillList)

    def Sort(self,evnt):
        self.anonymize = evnt.anon 

        if self.anonymize:
            anonTab = self.prefDlg.pages[0]
            anonDict = anonTab.anonList.GetAnonDict()
            self.dicomSorter.SetAnonRules(anonDict)
        else:
            self.dicomSorter.SetAnonRules(dict())

        # TODO: Get folder format
        dFormat = evnt.fields 

        # TODO: Keep Series
        keepSeries = True

        filenameMethod = int(self.config['FilenameFormat']['Selection'])

        if filenameMethod == 0:
            # Image (0001)
            fFormat = '%(ImageType)s (%(InstanceNumber)04d)'
        elif filenameMethod == 1:
            # Use the original filename
            fFormat = ''
            self.dicomSorter.keep_filename = original
            # Alternately we could pass None to dicomSorter
        elif filenameMethod == 2:
            # Use custom format
            fFormat = self.config['FilenameFormat']['FilenameString']
        
        self.dicomSorter.filename = fFormat
        self.dicomSorter.folders = dFormat
        self.dicomSorter.includeSeries = keepSeries

        outputDir = self.SelectOutputDir()

        if outputDir == None:
            return
        
        self.dicomSorter.Sort(outputDir,test=True,listener=self)

        self.Bind(EVT_COUNTER,self.OnCount)

    def OnCount(self,evnt):
        statusText = '%s / %s' % (evnt.Count,evnt.total)
        self.SetStatusText(statusText)

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

    def _MenuGenerator(self,parent,name,arguments):
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

    def _InitializeMenus(self):
        menubar = wx.MenuBar()

        file = [['&Open Directory','Ctrl+O',self.pathEditor.BrowsePaths],
                ['&Sort Images','Ctrl+S',self.Sort],
                '----',
                ['&Preferences...','Ctrl+,',self.OnPreferences],
                '----',
                ['&Exit','Ctrl+W',self.OnQuit]]

        self._MenuGenerator(menubar,'&File',file)

        help = [['About','',self.OnAbout],
                ['&Help','Ctrl+?',self.OnHelp]]

        self._MenuGenerator(menubar,'&Help',help)

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