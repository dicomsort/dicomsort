import gui

app = gui.DicomSort()
al = app.frame.prefDlg.pages['Anonymization'].anonList
app.MainLoop()
