import wx

app = wx.App(1)

w = wx.Config('dicomSort','suever')

w.Create()

defaultAnon = '{PatientsName:"ANON",PatientsAddress:"",PatientsBirthDate,""}'

w.Write('First','jonathan')
w.Write('Last','Jonathan')



app.MainLoop()


class AnonymizerConfig:

    def __init__(self):
        wx.Config('dicomSort','suever')

