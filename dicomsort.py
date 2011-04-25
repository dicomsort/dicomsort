#!/usr/bin/env python
import wx, wx.html
from wx.lib.dialogs import ScrolledMessageDialog

import os, dicom
import time
from threading import *
import re
import shutil
import string
import sys
import random

class ModFileConfig(wx.FileConfig):

    def __init__(self,app,vendor,filename):
        wx.FileConfig.__init__(self,app,vendor,filename)
        
    def GetAllEntries(self):
        for i in range(self.GetNumberOfEntries()):
            if i == 0:
                res = [self.GetFirstEntry()[1],]
            else:
                res.append(self.GetNextEntry(i)[1])
            
        return res



class App:

    def __init__(self):
        self.app = wx.App()
        
        self.exedir = os.path.dirname(sys.executable)
        
        global exedir

        exedir = self.exedir;

        self.anonConfig = ModFileConfig('DicomSort','Suever',os.path.join(exedir,'anon.inc'))
                
        
        self.frame = wx.Frame(None, -1, "DICOM Sorting Program", size=(550,450))
       
        if os.path.isfile(os.path.join(self.exedir,'DSicon.ico')):
            favicon = wx.Icon(os.path.join(self.exedir,'DSicon.ico'), 
                wx.BITMAP_TYPE_ICO, 16, 16)
        else:
            favicon = wx.Icon(os.path.join(sys.path[0],'DSicon.ico'),wx.BITMAP_TYPE_ICO,16,16);

        self.frame.SetIcon(favicon)
        
        self.root = wx.Panel(self.frame,-1,size=(550,450))

        self.createMenu() # Create the main menu

        self.listboxCreate(self.root)
        
        self.controlsCreate()
        
        self.loadDir = wx.Button(self.root, -1, label="Browse")#, pos=(375,10), size=(80,10))
        
        self.frame.Bind(wx.EVT_BUTTON, self.loadPush, id=self.loadDir.GetId())
        
        self.path = wx.TextCtrl(self.root, -1, "",style=wx.TE_PROCESS_ENTER)#, pos=(20,10), size=(350,20), 
            
        self.frame.Bind(wx.EVT_TEXT_ENTER, self.manLoadPush, self.path)
        
        self.apply = wx.Button(self.root, label="Sort Images")#, pos=(360,380), size=(120,10))
        
        self.apply.Bind(wx.EVT_BUTTON, self.processIms, self.apply)
        
        self.search = wx.SearchCtrl(self.root, -1, "",style=wx.TE_PROCESS_ENTER)#, size=(100,20))#, pos=(20,380), size=(200,20),
            
        
        self.frame.Bind(wx.EVT_TEXT, self.searchUpdate, self.search)
        self.frame.Bind(wx.EVT_TEXT_ENTER, self.focusProp, self.search)
        
        self.checkprivate = wx.CheckBox(self.root, -1, "Anonymize Output")#,pos=(320,300))
        self.checkprivate.SetValue(False)
        
        self.frame.Bind(wx.EVT_CHECKBOX, self.AnonCheck, self.checkprivate)
        
        self.checksameName = wx.CheckBox(self.root, -1, "Keep Original Filename")#, pos=(320,330))
        self.checksameName.SetValue(False)
        
        self.manageLayout()
        
        self.AnonymizeDisp()
        
        # Setup Frame properties
                
        self.frame.Show(True)
        self.frame.Center()
        self.frame.SetFocus()
        
        self.frame.CreateStatusBar()
        self.frame.SetStatusText("Ready...")
        
        #self.dt = wx.FileDropTarget()
        
        self.dt = FileDropTarget(self.path, self)
        self.path.SetDropTarget(self.dt)
                
            
        self.imworker = None;
        EVT_RESULT(self.frame,self.result)
        
        self.chars = re.compile('[^a-zA-Z0-9]+')
        self.chars2 = re.compile('^-|-\Z|^_|_\Z')
        
        self.app.MainLoop()
        try:
            self.anon.Destroy()
        except:
            pass
            
        try:
            self.app.Destroy()
        except:
            pass
        
    def AnonymizeDisp(self, *evnt):
        self.anon = wx.Frame(self.frame, -1, "Fields to Remove", size=(390,450),
            style=wx.DEFAULT_DIALOG_STYLE)
        self.anon.panel = wx.Panel(self.anon)
        
        self.anon.Bind(wx.EVT_CLOSE, self.AnonClose, id=self.anon.GetId())
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.anon.lb = wx.CheckListBox(self.anon.panel, -1,size=(250,300),choices=[])
        
        vbox.Add(self.anon.lb, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 20)

        self.anon.defbtn = wx.Button(self.anon.panel, -1, "Revert to Defaults")
        
        self.anon.Bind(wx.EVT_BUTTON, self.setDefault,id=self.anon.defbtn.GetId())
        
        vbox.Add(self.anon.defbtn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 20)
        
        self.anon.okbtn = wx.Button(self.anon.panel, -1, "Accept")
        self.anon.Bind(wx.EVT_BUTTON, self.AnonClose, id=self.anon.okbtn.GetId())
        
        vbox.Add(self.anon.okbtn, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP,20)        
        self.anon.panel.SetSizer(vbox)

                                
    def AnonCheck(self, *evnt):
    
        if(self.checkprivate.GetValue()):
            self.anon.Show(True)
            self.anon.CenterOnParent()
            
            self.anon.lb.Set(self.lb.prop.GetItems())
        
            try:
                self.anon.lb.SetCheckedStrings(self.currentAnon)
            except:
                pass
                
    def manageLayout(self):
        
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        vbox2 = wx.BoxSizer(wx.VERTICAL)
        vbox3 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        
        vbox1.Add(self.add, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 10)
        vbox1.Add(self.remove, 0,wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)
        vbox1.Add(self.up, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)
        vbox1.Add(self.down, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 15)
        
        vbox2.Add(self.sel, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vbox2.Add(self.lb.sel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)
        vbox2.Add(self.checkprivate, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP, 10)
        vbox2.Add(self.checksameName, 0, wx.ALIGN_LEFT | wx.LEFT | wx.TOP , 10)
        vbox2.Add(self.apply, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM | wx.TOP, 20)
        
        vbox4 = wx.BoxSizer(wx.VERTICAL)
        
        vbox4.Add(self.lb, 0, wx.ALIGN_CENTER_HORIZONTAL)
        vbox4.Add(self.lb.prop, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, 10)
        vbox4.Add(self.search, 0, wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL | wx.LEFT | wx.RIGHT , 40)
        
        hbox1.Add(self.path, 1, wx.LEFT | wx.RIGHT | wx.TOP, 5)
        hbox1.Add(self.loadDir, 0, wx.LEFT | wx.RIGHT | wx.TOP, 10)
        
        hbox2.Add(vbox4, 1, wx.EXPAND | wx.BOTTOM, 10)
        hbox2.Add(vbox1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.TOP, 40)
        hbox2.Add(vbox2, 1, wx.EXPAND)

        vbox3.Add(hbox1, 0, wx.EXPAND | wx.LEFT | wx.TOP | wx.BOTTOM | wx.RIGHT, 15)
        vbox3.Add(hbox2, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
        
        self.root.SetSizer(vbox3)
        
    def setDefault(self, *evnt):
    
        self.anon.lb.SetCheckedStrings(self.defaultAnon)
        
    def AnonClose(self, *evnt):
    
        self.currentAnon = self.anon.lb.GetCheckedStrings()
        self.anon.Show(False)
        
    def listboxCreate(self, parent):
        """Creates the two main listboxes for this program"""
        self.lb = wx.StaticText(parent, -1, "DICOM Properties")#, pos=(65,40))
        self.lb.prop = wx.ListBox(parent, -1)#, (20,60), (200,300))
        self.frame.Bind(wx.EVT_LISTBOX_DCLICK, self.AddCallback, id=self.lb.prop.GetId())
        self.sel = wx.StaticText(parent, -1, "Properties to Use")#, pos=(375,40))
        self.lb.sel = wx.ListBox(parent, -1)#, (320,60), (200,225))
        self.frame.Bind(wx.EVT_LISTBOX_DCLICK, self.removeCallback, id=self.lb.sel.GetId())
                       
    def controlsCreate(self):
    
        self.add = wx.Button(self.root, -1, label=">>")
        self.remove = wx.Button(self.root, -1, label="<<")
        self.up = wx.Button(self.root, -1, label="Up")
        self.down = wx.Button(self.root, -1, label="Dn")
                
        self.frame.Bind(wx.EVT_BUTTON, self.AddCallback,id=self.add.GetId())
        self.frame.Bind(wx.EVT_BUTTON, self.removeCallback, id=self.remove.GetId())
        self.frame.Bind(wx.EVT_BUTTON, self.moveUpCallback, id=self.up.GetId())
        self.frame.Bind(wx.EVT_BUTTON, self.moveDownCallback, id=self.down.GetId())

                
    def createMenu(self):
        """Generate the Menubar for the GUI"""      
        menubar = wx.MenuBar()
        
        file = wx.Menu()
        open = wx.MenuItem(file, -1, "&Open Directory\tCtrl+O")
        sort = wx.MenuItem(file, -1, "&Sort Images\tCtrl+S")
        quit = wx.MenuItem(file, -1, '&Exit\tCtrl+W')

        file.AppendItem(open)
        file.AppendItem(sort)
        file.AppendSeparator()
        file.AppendItem(quit)
        
        edit = wx.Menu()
        
        add = wx.MenuItem(edit, -1, "&Add Property\t=")
        rem = wx.MenuItem(edit, -1, "&Remove Property\t-")

        edit.AppendItem(add)
        edit.AppendItem(rem)

        edit.Append(-1,"Promote Property")
        edit.Append(-1,"Demote Property")
        
        help = wx.Menu()
        about = wx.MenuItem(help, -1, "About")
        helpmenu = wx.MenuItem(help, -1, "&Help\tCtrl+?")
        help.AppendItem(about)
        help.AppendItem(helpmenu)
        
        menubar.Append(file, "&File")
        menubar.Append(edit, "&Edit")
        menubar.Append(help, "&Help")
        
        self.frame.SetMenuBar(menubar)
        self.frame.Bind(wx.EVT_MENU, self.loadPush, id=open.GetId())
        self.frame.Bind(wx.EVT_MENU, self.processIms, id=sort.GetId())
        self.frame.Bind(wx.EVT_MENU, self.OnQuit, id=quit.GetId())
        self.frame.Bind(wx.EVT_MENU, self.AddCallback, id=add.GetId())
        self.frame.Bind(wx.EVT_MENU, self.removeCallback, id=rem.GetId())
        self.frame.Bind(wx.EVT_MENU, self.about, id=about.GetId())
        self.frame.Bind(wx.EVT_MENU, self.helpBox, id=helpmenu.GetId())
               
    def loadPush(self, *evnt):
        """Action when a new Directory is selected"""

        
        path = wx.DirDialog(self.frame, "Please Select Directory", defaultPath='C:\\')
        path.CenterOnParent()
        
        if(path.ShowModal() == wx.ID_OK):
            self.path.SetValue(path.GetPath())
            self.lb.sel.Set([])
            self.walkDirs(path.GetPath())
            self.frame.SetStatusText("Ready...")
            
        path.Destroy()
            
    def manLoadPush(self, *evnt):
        """When the user enters a directory manually"""
        
        dir = self.path.GetValue()
        
        if(os.path.isdir(dir)):
            self.lb.sel.Set([])
            self.walkDirs(dir)
            self.frame.SetStatusText("Ready...")
        else:
            dlg = x.MessageDialog(None, "The Directory "+str(dir)+" does not exist!",
                "Invalid Location",wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            
    def walkDirs(self,basedir):
        
        """Walk through the directory tree looking for all files"""
        
        example = ''
                
        for root, dirs, files in os.walk(basedir):
            for f in files:            
                if(f[0] != '.'):
                    example = (os.path.join(root,f))
                    break
                    break
                
        if(example):
            try:
                self.dcm = dicom.ReadFile(example.encode("UTF-8"))
                if(len(self.dcm) == 1):
                    dlg=wx.MessageDialog(None,"Plase Select a Directory that only contains DICOMs","Error",
                    wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                else:
                    self.lb.prop.Set(self.dcm.dir(''))
                    self.search.SetValue('')
                    self.search.SetFocus()
                    self.defPrivateFields()
            except:
                m = wx.MessageDialog(None,"Plase Select a Directory that only contains DICOMs","Error",
                    wx.OK | wx.ICON_ERROR)
                m.ShowModal()
                m.Destroy()
                    
    def defPrivateFields(self, *evnt):

        if self.anonConfig.GetNumberOfEntries() == 0:
            

            anonFields = ['PatientsName','PatientsAddress','PatientsBirthDate']
        
        self.defaultAnon = list()
        
        for field in anonFields:
            field = string.strip(field)
            if(hasattr(self.dcm, field)):
                self.defaultAnon.append(field)
        self.currentAnon = self.defaultAnon
                
        try:
            close(anonFields)
        except:
            pass
            
    def RestoreAnonDefaults(self,*evnt):
        for field in self.anonConfig.GetAllEntries():
            if hasattr(self.dcm,field):
                print field

    def ResetAnonEntries(self,*evnt):
        self.anonConfig.DeleteAll()
        [self.anonConfig.Write(d,'') for d in ['PatientsName','PatientsAddress']]
        
    def OnQuit(self, *evnt):
        """Exit Application"""
        dialog = wx.MessageDialog(None, "Are you sure you want to exit?", "Confirmation",
            wx.YES_NO | wx.ICON_QUESTION)
            
        dialog.CentreOnParent(wx.BOTH)
            
        retCode = dialog.ShowModal()
        
        dialog.Destroy()
        if(retCode == wx.ID_YES):           
            self.frame.Destroy()
            #self.app.Destroy()
        
    def AddCallback(self,*evnt):
        """Add property to list"""
        
        prop2add = self.lb.prop.GetStringSelection()
        
        if(prop2add != ""):
            self.lb.sel.Append(prop2add)
        
    def removeCallback(self,*evnt):
        """Remove property from list"""
        
        index = self.lb.sel.GetSelection()
        
        try:
            self.lb.sel.Delete(index)
            self.lb.sel.Select(index-1)
        except:
            pass
        
    def moveUpCallback(self,*evnt):
        
        index = self.lb.sel.GetSelection()
        prop = self.lb.sel.GetStringSelection()
        
        if(index != 0 and index!= ""):
            try:
                self.lb.sel.Delete(index)
                self.lb.sel.Insert(prop,index-1)
                self.lb.sel.Select(index-1)
            except:
                pass
        
    def moveDownCallback(self,*evnt):
        
        index = self.lb.sel.GetSelection()
        prop = self.lb.sel.GetStringSelection()
        
        if(index < len(self.lb.sel.GetItems())-1):
            try:
                self.lb.sel.Delete(index)
                self.lb.sel.Insert(prop,index+1)
                self.lb.sel.Select(index+1)
            except:
                pass
            
    def focusProp(self, *evnt):
        self.lb.prop.SetFocus()
        self.lb.prop.Select(0)
        
    def processIms(self, *evnt):
    
        outPath = wx.DirDialog(None, "Please Select Output Directory",
            defaultPath=self.path.GetValue())
       
        if(outPath.ShowModal() == wx.ID_OK):
               
            if not self.imworker:
                self.imworker = WorkerThread(self.frame, self, outPath.GetPath())
                
        outPath.Destroy()
                
    def result(self, event):
    
        if(event.data == "COMPLETE"):
            self.frame.SetStatusText(event.data)
            self.imworker = None
        else:
            self.frame.SetStatusText("Processing Image..."+str(event.data))
        
    def searchUpdate(self, *evnt):
    
        try:
            self.lb.prop.Set(self.dcm.dir(self.search.GetValue()))
        except:
            pass
            
    def consecNum(self,n,digits):
        while(len(n) < digits):
            n = '0' + n
            
        return n
        
    def about(self, *evnt):
    
        description = ("      Program designed to sort DICOM images       \n"+
                       "     into directories based upon DICOM header     \n"+
                       "      information. The program also provides      \n"+
                       "       additional functionality such as the       \n"+
                       "anonymization of DICOM images for patient privacy.")
        
        info = wx.AboutDialogInfo()
        
        info.SetIcon(wx.Icon(os.path.join(self.exedir,'dsnoshad.ico'),
            wx.BITMAP_TYPE_ICO))
        info.SetName('DICOM Sorting')
        info.SetVersion('1.3')
        info.SetDescription(description)
        info.SetCopyright('(C) 2010 Jonathan Suever')
        info.SetWebSite('http://www.suever.net')
        
        wx.AboutBox(info)
        
    def helpBox(self, *evnt):
    
        handle = open(os.path.join(self.exedir,'help.inc'),"r")
        helpText = handle.read()
        
        handle.close()
    
        #helpText = open(os.path.join(self.exedir,'help.inc'),"r").read()
        
        self.hb = wx.Dialog(self.frame, -1, "DICOM Sorting Help",
            style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|
            wx.TAB_TRAVERSAL)
            
        self.hwin = HtmlWindow(self.hb, -1, size=(400,20))
        
        self.hwin.SetPage(helpText)
        btn = self.hwin.FindWindowById(wx.ID_OK)
        irep = self.hwin.GetInternalRepresentation()
        
        self.hwin.SetSize((irep.GetWidth(), int(irep.GetHeight()/4)))
        self.hb.Show(True)
        self.hb.SetClientSize(self.hwin.GetSize())
        self.hb.CenterOnParent(wx.BOTH)
        self.hb.SetFocus()
        
        self.hb.Bind(wx.EVT_CLOSE, self.hbquit, id=self.hb.GetId())
        
    def hbquit(self, *evnt):
        self.hb.Destroy()
        
class WorkerThread(Thread):

    def __init__(self, notify_window, app, outPath):
    
        self.appLink = app
        self.outPath = outPath
    
        Thread.__init__(self)
        self._notify_window = notify_window
        self.start()
        
    def run(self):
        """Run Worker Thread."""
        
        app = self.appLink
        outputPath = self.outPath
        
        parameters = app.lb.sel.GetItems()
      

                    wx.PostEvent(self._notify_window, ResultEvent(count))
                    
        wx.PostEvent(self._notify_window, ResultEvent("COMPLETE"))
                  
class ResultEvent(wx.PyEvent):

    def __init__(self, data):
    
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        
        
class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size):
        wx.html.HtmlWindow.__init__(self,parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()
            
class FileDropTarget(wx.FileDropTarget):
    def __init__(self,obj,general):
        wx.FileDropTarget.__init__(self)
        self.obj = obj
        self.main = general
        
    def OnDropFiles(self, x, y, filenames):
        self.obj.SetValue(filenames[0])
        self.main.manLoadPush()

def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)
           
EVT_RESULT_ID = wx.NewId()
        
app = App()
