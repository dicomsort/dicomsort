import dicomsorter
import wx.py as py
import os
import re
import wx
import wx.lib.newevent
import wx.py
import configobj
import settings

defaultConfig = {'Anonymization':
                        {'Fields':['PatientsName','PatientID'],
                        'Replacements':
                            {'PatientsName':'ANONYMOUS'}},
                 'FilenameFormat':
                        {'Filename':'%(ImageType)s (%(InstanceNumber)04d)'}}

def throw_error(message,title='Error'):
    dlg = wx.MessageDialog(None,message,title,wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()
    dlg.Destroy()

#TODO: Add status bar that include: Percentage of Transfer, Number of Threads
#TODO: Add sort/anonymize buttons
#TODO: Generate Interface between field chooser and dirFormat strings

# Event Definitions
PathEvent,      EVT_PATH            = wx.lib.newevent.NewEvent()
PopulateEvent,  EVT_POPULATE_FIELDS = wx.lib.newevent.NewEvent()

class DicomSort(wx.App):
    def __init__(self,debug=0):
        wx.App.__init__(self)

        if debug:
            self.debug = wx.Frame(None,-1,'DEBUGGER',size=(700,500),pos=(700,0))
            self.crust = wx.py.crust.Crust(self.debug)
            self.debug.Show()

        self.frame = MainFrame(None,-1,size=(700,500))
        self.frame.Show()

        self.SetTopWindow(self.frame)

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

        self.prefDlg = settings.PreferenceDlg(None,-1,"DicomSort Preferences",
                            config = self.config, size=(400,400))

    def _initialize_components(self):
        global DEBUG

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.pathEditor = PathEdit(self,-1)
        vbox.Add(self.pathEditor,0,wx.EXPAND)

        self.selector = FieldSelector(self,titles=['DICOM Properties',
                                                   'Properties to Use'])
        vbox.Add(self.selector,1,wx.EXPAND)

        self.SetSizer(vbox)

        self.pathEditor.Bind(EVT_PATH,self.fill_list)

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

        file = [['&Open Directory','Ctrl+O',self.pathEditor.browse_paths],
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

    def fill_list(self,evnt):
        self.dicomSorter.pathname = evnt.path
        try:
            fields = self.dicomSorter.GetAvailableFields()
        except dicomsorter.DicomFolderError:
            errMsg = ''.join([evnt.path,' contains no DICOMs'])
            throw_error(errMsg,'No DICOMs Present')
            return

        self.selector.set_options(fields)

        # This is clunky
        # TODO: Change PrefDlg to a dict
        self.prefDlg.pages[0].SetDicomFields(fields)

        self.Notify(PopulateEvent,fields=fields)

    def Notify(self,evntType,**kwargs):
        event = evntType(**kwargs)
        wx.PostEvent(self,event)


class PathEdit(wx.Panel):

    def __init__(self,*args,**kwargs):
        wx.Panel.__init__(self,*args,**kwargs)
        self._initialize_controls()
        self.path = ''
        self.Bind(wx.EVT_TEXT_ENTER,self.validate_path,self.edit)

    def validate_path(self,*evnt):
        path = os.path.abspath(self.edit.GetValue())

        # update the box with the absolute path
        self.edit.SetValue(path)

        if os.path.isdir(path):
            self.path = path
            self.notify()
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

        self.browse.Bind(wx.EVT_BUTTON, self.browse_paths)

        self.SetSizer(hbox)

    def notify(self,*evnt):
        global PathEvent
        event = PathEvent(path=self.path)
        wx.PostEvent(self,event)

    def browse_paths(self,*evnt):
        # Open the dialog and search
        path = wx.DirDialog(self.GetParent(),"Please Select Directory",
                                    defaultPath=self.path)
        path.CenterOnParent()

        if path.ShowModal() == wx.ID_OK:
            self.edit.SetValue(path.GetPath())
            self.validate_path()

        path.Destroy()
