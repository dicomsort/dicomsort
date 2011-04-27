import os
import configobj
import dicomsorter
import sys
import re
import traceback
import urllib
import urllib2
import widgets
import wx
import wx.lib.newevent

configFile = 'dicomSort.ini'

__version__ = '2.0.0'
Version = (2,0,0)

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
                     'Selection':0},
                 'Miscpanel':
                    {'KeepSeries':'True'}}

# Define even
PathEvent,EVT_PATH = wx.lib.newevent.NewEvent()
PopulateEvent,EVT_POPULATE_FIELDS = wx.lib.newevent.NewEvent()
SortEvent,EVT_SORT = wx.lib.newevent.NewEvent()
CounterEvent,EVT_COUNTER = wx.lib.newevent.NewEvent()

def ExceptHook(type,value,tb):
    dlg = CrashReporter(type,value,tb)
    dlg.ShowModal()

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
        self.SetTopWindow(self.frame)
        self.frame.Show()

        sys.excepthook = ExceptHook

    def MainLoop(self,*args):
        wx.App.MainLoop(self,*args)


from gui import preferences

class CrashReporter(wx.Dialog):
    def __init__(self,type,value,tb):
        super(CrashReporter,self).__init__(None,-1,'DicomSort Crash Reporter',
                    size=(400,400))
        self.type = type
        self.value = value
        self.tb = tb

        self.traceback = '\n'.join(traceback.format_exception(type,value,tb))

        self.Create()

    def Create(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        heading = wx.StaticText(self,-1,"Epic Fail")
        heading.SetFont(wx.Font(12,wx.DEFAULT,wx.NORMAL, wx.BOLD))

        vbox.Add(heading,0,wx.LEFT | wx.TOP,15)

        text = ''.join(['Dicom Sorting had a problem and crashed.\n',
                        'In order to help diagnose the problem, you can send a '
                        'crash report.' ])

        static = wx.StaticText(self,-1,text)
        vbox.Add(static,0,wx.ALL,15)

        vbox.Add(wx.StaticText(self,-1,'Comments:'),0,wx.LEFT,15)

        self.comments = wx.TextCtrl(self,style=wx.TE_MULTILINE)

        defComments = '\n\n\n--------------DO NOT EDIT BELOW ------------\n'

        self.comments.SetValue(defComments+self.traceback)
        vbox.Add(self.comments,1,wx.EXPAND|wx.LEFT|wx.RIGHT,15)

        label = 'Email me when a fix is available'
        self.email = wx.CheckBox(self,-1,label=label)
        vbox.Add(self.email,0,wx.LEFT | wx.RIGHT | wx.TOP, 15)

        self.email.Bind(wx.EVT_CHECKBOX,self.OnEmail)

        self.emailAddress = wx.TextCtrl(self,-1,'Enter your email address here',
                size=(200,-1))
        self.emailAddress.Enable(False)

        vbox.Add(self.emailAddress,0,wx.LEFT | wx.RIGHT, 35)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.sender = wx.Button(self,-1,"Send Report")
        self.cancel = wx.Button(self,-1,"Cancel")

        self.sender.Bind(wx.EVT_BUTTON,self.Report)
        self.cancel.Bind(wx.EVT_BUTTON,self.OnCancel)

        hbox.Add(self.cancel,0,wx.RIGHT,10)
        hbox.Add(self.sender,0,wx.RIGHT,15)

        vbox.Add(hbox,0,wx.TOP | wx.BOTTOM | wx.ALIGN_RIGHT,10)

        self.SetSizer(vbox)

    def OnCancel(self,*evnt):
        self.Destroy()

    def OnEmail(self,*evnt):
        if self.email.IsChecked():
            self.emailAddress.Enable()
        else:
            self.emailAddress.Enable(False)

    def Report(self,*evnt):
        if self.email.IsChecked():
            email = self.ValidateEmail()
        else:
            email = None

        url = 'http://www.suever.net/software/dicomSort/bug_report.php'
        values = {'OS':sys.platform,
                  'version':__version__,
                  'email':email,
                  'comments':self.comments.GetValue().strip('\n')}

        data = urllib.urlencode(values)
        resp = urllib2.urlopen(url,data)
        self.OnCancel()

    def ValidateEmail(self):
        email = self.emailAddress.GetValue()
        print email

        regex = '[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}'

        if not re.search(regex,email,re.UNICODE|re.IGNORECASE):
            ThrowError('Please enter a valid email address')

        return email

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

        # Set Frame icon
        if os.path.isfile(os.path.join(sys.executable,'DSicon.ico')):
            self.exedir = sys.executable
        else:
            self.exedir = sys.path[0]

        path = os.path.join(self.exedir,'DSicon.ico')
        icon = wx.Icon(path,wx.BITMAP_TYPE_ICO,16,16)
        self.SetIcon(icon)

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

        if self.dicomSorter.IsSorting():
            return

        self.anonymize = evnt.anon 

        if self.anonymize:
            anonTab = self.prefDlg.pages['Anonymization']
            anonDict = anonTab.anonList.GetAnonDict()
            self.dicomSorter.SetAnonRules(anonDict)
        else:
            self.dicomSorter.SetAnonRules(dict())

        dFormat = evnt.fields 

        keepSeries = eval(self.config['Miscpanel']['KeepSeries'])

        filenameMethod = int(self.config['FilenameFormat']['Selection'])

        if filenameMethod == 0:
            # Image (0001)
            fFormat = '%(ImageType)s (%(InstanceNumber)04d)'
        elif filenameMethod == 1:
            # Use the original filename
            fFormat = ''
            self.dicomSorter.keep_filename = True
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

        # Use this for testing
        # self.dicomSorter.Sort(outputDir,test=True,listener=self)

        # Use for the real deal
        self.dicomSorter.Sort(outputDir,listener=self)

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
        widgets.AboutDlg()

    def OnHelp(self,*evnt):
        handle = open(os.path.join(self.exedir,'help.inc'),"r")
        helpText = handle.read()

        widgets.HelpDlg(self,text=helpText)

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

    def LoadDebug(self,*evnt):
        size = self.Size
        pos = self.Position

        pos = (pos[0]+size[0],pos[1])

        self.debug = wx.Frame(None,-1,'DicomSort DEBUGGER',size=(700,500),pos=pos)
        self.crust = wx.py.crust.Crust(self.debug)
        self.debug.Show()

    def _InitializeMenus(self):
        menubar = wx.MenuBar()

        file = [['&Open Directory','Ctrl+O',self.pathEditor.BrowsePaths],
                '----',
                ['&Preferences...','Ctrl+,',self.OnPreferences],
                '----',
                ['&Exit','Ctrl+W',self.OnQuit]]

        self._MenuGenerator(menubar,'&File',file)

        win = [['&Debug Window','Ctrl+D',self.LoadDebug],]

        self._MenuGenerator(menubar, '&Window', win)

        help = [['About','',self.OnAbout],
                ['&Help','Ctrl+?',self.OnHelp]]

        self._MenuGenerator(menubar,'&Help',help)

        self.SetMenuBar(menubar)


    def FillList(self,evnt):
        self.dicomSorter.pathname = evnt.path
        try:
            fields = self.dicomSorter.GetAvailableFields()
        except dicomsorter.DicomFolderError:
            errMsg = ''.join([';'.join(evnt.path),' contains no DICOMs'])
            ThrowError(errMsg,'No DICOMs Present')
            return

        self.selector.SetOptions(fields)

        # This is clunky
        # TODO: Change PrefDlg to a dict
        self.prefDlg.pages['Anonymization'].SetDicomFields(fields)

        self.Notify(PopulateEvent,fields=fields)

    def Notify(self,evntType,**kwargs):
        event = evntType(**kwargs)
        wx.PostEvent(self,event)