import gui
import wx

def callback(evnt):
	print evnt.path

app = wx.App(0)
f = gui.MainFrame(None,-1,'TestGUI')
f.Show()
app.MainLoop()
