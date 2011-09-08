from distutils.core import setup
import py2exe
import os
import gui
import shutil

data = [('',['build/DSicon.ico',]),
		('',['build/msvcp90.dll',])]

NAME = 'DICOM Sort'
VER	= gui.__version__

OUTDIR = os.path.expanduser(os.path.join('~','Desktop',''.join([NAME,' ',VER])))
		
setup(
	name = NAME,
	version = VER,
	description = 'A DICOM Sorting Utility',
	author = 'Jonathan Suever',
	packages=['gui',],
    options = {'py2exe': {'bundle_files': 1,
						  'dist_dir':OUTDIR}},
	data_files = data,
    windows = [{"script":'DicomSort.pyw',
				"icon_resources":[(1,"DSicon.ico")]}],
    zipfile = None,
)

shutil.rmtree(os.path.join(OUTDIR,'tcl'))
os.remove(os.path.join(OUTDIR,'w9xpopen.exe'))
