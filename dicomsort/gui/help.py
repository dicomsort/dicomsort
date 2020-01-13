import wx.html

helpHTML = """
<span style="fontsize:9px;"> <center><h3>DICOM Sorting Help</h3></center> <br>
<strong><u>Introduction</u></strong><br> This utility will sort images based
upon DICOM header information.  The user is able to sort by multiple fields
which are sent to the program when a directory of DICOM images is selected.
<br><br> <strong><u>Operation</u></strong><br> You must first Browse for the
directory that contains the DICOM images to be sorted. <strong>This folder
should preferably be the DICOM folder on the CD</strong> <br><br> When the
images are loaded the available DICOM header values are listed in the
<strong>DICOM Properties</strong> listbox. Double-click or push the
<strong>&gt;&gt;</strong> button to add the selected property to the listbox on
the right.  <br> The properties that are added to the listbox on the right are
then used to determine the directory structure as shown below: <br><br>
<strong>/First Listbox Entry/Second Listbox Entry/ (etc.)</strong> <br><br> It
is important to note that you will select the output directory (signified by
'~' above) when you click on the <strong>Sort Button</strong>.  <br><br> You
can also change the ordering of the sorting parameters using the <strong>Up and
Down Buttons</strong> located between the two boxes.  <br><br> To remove a
property from the parameter box, use the <strong>&lt;&lt;</strong> button after
selecting the property to remove or double-click the entry.  Once you are
satisfied with your parameter selection, click on the <strong>Sort
Button</strong> to perform the requested operation.  <br><br> Similarly to
previous versions of the sorting program, the program will always additionally
sort the data by <strong>Series Number</strong> and <strong>Series
Description</strong>.  The actual image file name is determined by the
<strong>Instance Number</strong> and <strong>Image Type</strong> (Magnitude,
Phase, or Other).  <br><br> The number of images processed is shown in the
lower left-hand corner of the application.  <br><br> <strong><u>Optional
Features</u></strong><br> Version 1.1 now provides the user the ability to
remove sensitive patient data from the DICOM metadata. To do this, select the
<strong>Anonymize</strong> checkbox.  Pressing this button will bring up a
window that will allow you to select which fields you do not want included in
the output images. You can always revert back to the default properties using
the <strong>Revert to Defaults</strong> button.  <br><br> If you wish to change
the properties that are considered to be private by default, you can edit the
anon.inc file located in the application directory. Just edit this file using
any text editor and make sure to include one field per line in the file. The
next time the program is loaded, these fields will be used as the default
anonymous fields.  <br><br> Another option is to use the original filenames as
the input files rather than renaming based upon the image type. This plays an
important role if the analysis program to be used requires a certain naming
convention. Names will be preserved when the checkbox is ticked.  <br><br>
<strong><u>Future Directions</u></strong> <ul> <li>Be able to handle selected
folders that contain more images than just DICOM images (create an
exception).</li> <li>Implement a preview of the values of selected DICOM
properties</li> </ul>
"""


class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()


class HelpDlg(wx.Dialog):

    def __init__(self, parent=None, **kwargs):

        super(HelpDlg, self).__init__(
            parent, -1, "DICOM Sorting Help",
            style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER | wx.TAB_TRAVERSAL
        )

        self.hwin = HtmlWindow(self, -1, size=(400, 200))

        self.hwin.SetPage(helpHTML)
        irep = self.hwin.GetInternalRepresentation()

        self.hwin.SetSize((irep.GetWidth(), int(irep.GetHeight() / 4)))
        self.Show()

        self.SetClientSize(self.hwin.GetSize())
        self.CenterOnParent(wx.BOTH)
        self.SetFocus()

        self.Bind(wx.EVT_CLOSE, self.close)

    def close(self, *_):
        self.Destroy()
