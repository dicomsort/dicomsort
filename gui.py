import dicomsorter

import os
import wx
import wx.lib.newevent

PathEvent,EVT_PATH = wx.lib.newevent.NewEvent()

class MainFrame(wx.Frame):

	def __init__(self,*args,**kwargs):
		wx.Frame.__init__(self,*args,**kwargs)
		self._initialize_components()

		# Use os.getcwd() for now
		self.dicomSorter = dicomsorter.DicomSorter()

	def _initialize_components(self):
		vbox = wx.BoxSizer(wx.VERTICAL)

		self.pathEditor = PathEdit(self,-1)
		vbox.Add(self.pathEditor,0,wx.EXPAND)

		self.selector = FieldSelector(self,titles=['DICOM Properties',
												   'Properties to Use'])
		vbox.Add(self.selector,1,wx.EXPAND)

		self.SetSizer(vbox)

		self.pathEditor.Bind(EVT_PATH,self.fill_list)

	def fill_list(self,evnt):
		self.dicomSorter.pathname = evnt.path
		fields = self.dicomSorter.get_available_fields()
		self.selector.set_options(fields)


class AnonymizerList(wx.CheckListBox):

	def __init__(self,parent,id=-1,size=(250,300),choices=[]):
		wx.CheckListBox.__init__(self,parent,id,size,choices)

	def revert(self):
		return

	def set_as_default(self):
		return

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
			dlg = wx.MessageDialog(None,errorMsg,'Invalid Location',
									wx.OK | wx.ICON_ERROR)
			dlg.ShowModal()
			dlg.Destroy()

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

class FieldSelector(wx.Panel):

	def __init__(self,parent,id=-1,size=(250,300),choices=[],titles=['','']):
		wx.Panel.__init__(self,parent,id=id,size=size)

		self.choices = choices
		self.titles = titles

		self._initialize_controls()

	def _initialize_controls(self):

		self.titleL		= wx.StaticText(self,-1,self.titles[0])
		self.options	= wx.ListBox(self,-1,choices=self.choices)

		self.titleR		= wx.StaticText(self,-1,self.titles[1])
		self.selected	= wx.ListBox(self,-1,choices=[])

		# Setup double-click callbacks
		self.options.Bind(wx.EVT_LISTBOX_DCLICK, self.select_item)
		self.selected.Bind(wx.EVT_LISTBOX_DCLICK, self.deselect_item)

		# Setup controls:
		self.bAdd = wx.Button(self,-1,label=">>")
		self.bRemove = wx.Button(self,-1,label="<<")
		self.bUp = wx.Button(self,-1,label="Up")
		self.bDown = wx.Button(self,-1,label="Down")

		self.bAdd.Bind(wx.EVT_BUTTON, self.select_item)
		self.bRemove.Bind(wx.EVT_BUTTON, self.deselect_item)
		self.bUp.Bind(wx.EVT_BUTTON, self.promote_selection)
		self.bDown.Bind(wx.EVT_BUTTON, self.demote_selection)

		self._initialize_layout()

	def _initialize_layout(self):
		# BoxSizer containing the options to select
		vboxOptions = wx.BoxSizer(wx.VERTICAL)

		vboxOptions.Add(self.titleL, 0, wx.ALIGN_CENTER_HORIZONTAL)
		vboxOptions.Add(self.options, 1, 
						wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, 10)

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

	def promote_selection(self,*evnt):
		self._move_selection(-1)

	def demote_selection(self,*evnt):
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

	def select_item(self,*evnt):
		item = self.options.GetStringSelection()
		self.selected.Append(item)

	def deselect_item(self,*evnt):
		index = self.selected.GetSelection()
		self.selected.Delete(index)

		self.selected.Select(index-1)

	def set_titles(self,titleL,titleR):
		self.leftBox

	def set_options(self,optionList=[]):
		# clear 
		self.options.Clear()
		self.options.InsertItems(optionList,0)

		# TODO: Future checks to make sure that fields are in this

		

	
