import dicomsort
import os
import sys

from cx_Freeze import setup, Executable

ICON_DIR = 'icons'
ICO_FILE = os.path.join(ICON_DIR, 'DSicon.ico')
ICNS_FILE = os.path.join(ICON_DIR, 'DSicon.icns')

NAME = 'DICOM Sort'
URL = 'https://dicomsort.com'

base = None

if sys.platform == 'darwin':
    EXE = 'DICOM Sort.app'
    ICON = ICNS_FILE
else:
    EXE = 'DicomSort.exe'
    ICON = ICO_FILE


if sys.platform == 'win32':
    OUTDIR = os.path.join('dist', ''.join([NAME, ' ', dicomsort.__version__]))
else:
    OUTDIR = os.path.join('dist', NAME)


def shortcut(name, executable, type, directory):
    target = "[TARGETDIR]{}".format(executable)
    return (
         type,        # Shortcut
         directory,   # Directory_
         name,        # Name
         "TARGETDIR", # Component_
         target,      # Target
         None,        # Arguments
         None,        # Description
         None,        # Hotkey
         None,        # Icon
         None,        # IconIndex
         None,        # ShowCmd
         'TARGETDIR'  # WkDir
     )

setup(
    name=NAME,
    version=dicomsort.__version__,
    description='A DICOM Sorting Utility',
    options={
      'build': {
          'build_exe': OUTDIR
      },
      'bdist_msi': {
          'data': {
              'Shortcut': [
                  shortcut(NAME, 'DicomSort.exe', 'DesktopShortcut', 'DesktopFolder'),
                  shortcut(NAME, 'DicomSort.exe', 'ApplicationStartMenuShortcut', 'StartMenuFolder')
              ]
          }
      },
      'bdist_exe': {
          'include_msvcr': True,
          'include_files': [ICO_FILE, ]
      },
      'bdist_mac': {
          'iconfile': ICNS_FILE
      },
      'bdist_dmg': {
          'volume_label': "%s-%s" % (NAME, dicomsort.__version__)
      }
    },
    entry_points={
        'console_scripts': [
            'dicomsort = dicomsort.gui:main',
        ],
    },
    executables=[
        Executable(script='bin/dicomsort.py', base=base, icon=ICON, shortcutName='DICOM Sort')
    ]
)
