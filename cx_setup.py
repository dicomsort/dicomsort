from cx_Freeze import setup, Executable
import os
import shutil
import sys
import gui

base = None
if sys.platform == 'win32':
    base = "Win32GUI"
    ICON = 'DSicon.ico'
    EXE = 'DicomSort.exe'

if sys.platform == 'darwin':
    ICON = 'DSicon.icns'
    EXE = 'DICOM Sort.app'

includefiles = [ICON,]

NAME = 'DICOM Sort'
VERSION = gui.__version__
ID = '{{6638951C-0E99-4FAF-AAF1-B283912E7DE8}'
URL = 'https://dicomsort.com'

if sys.platform == 'darwin':
    OUTDIR = os.path.join('dist',NAME)
else:
    OUTDIR = os.path.join('dist', ''.join([NAME, ' ', VERSION]))

shortcut_table = [
    ("DesktopShortcut",          # Shortcut
     "DesktopFolder",            # Directory_
     NAME,                       # Name
     "TARGETDIR",                # Component_
     "[TARGETDIR]DicomSort.exe", # Target
     None,                       # Arguments
     None,                       # Description
     None,                       # Hotkey
     None,                       # Icon
     None,                       # IconIndex
     None,                       # ShowCmd
     'TARGETDIR'                 # WkDir
     ),
    ("ApplicationStartMenuShortcut",
     "StartMenuFolder",
     NAME,
     "TARGETDIR",
     "[TARGETDIR]DicomSort.exe",
     None,
     None,
     None,
     None,
     None,
     None,
     'TARGETDIR'
    )
]

msi_data = {
    "Shortcut": shortcut_table
}

setup(name = NAME,
      version = VERSION,
      description = 'A DICOM Sorting Utility',
      options = {
        'build': {
            'build_exe': OUTDIR
        },
        'bdist_msi': {
            'data': msi_data
        },
        'bdist_exe': {
            'include_msvcr': True,
            'include_files': includefiles
        },
        'bdist_mac': {
            'iconfile': ICON
        },
        'bdist_dmg': {
            'volume_label': "%s-%s" % (NAME, VERSION)
        }
      },
      executables = [
          Executable(
              script = 'DicomSort.pyw',
              base = base,
              icon = ICON,
              shortcutName = 'DICOM Sort'
          ),
      ])
