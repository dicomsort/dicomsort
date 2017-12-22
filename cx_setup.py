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
VER = gui.__version__
ID = '{{6638951C-0E99-4FAF-AAF1-B283912E7DE8}'
URL = 'https://dicomsort.com'

if sys.platform == 'darwin':
    OUTDIR = os.path.join('dist',NAME)
else:
    OUTDIR = os.path.join('dist', ''.join([NAME, ' ', VER]))

build_options = {
    "build_exe": OUTDIR
}

bdist_exe_options = {
    "include_msvcr": True,
    "include_files": includefiles
}

exe = Executable(
    script='DicomSort.pyw',
    base=base,
    targetName=EXE,
    icon=ICON)

bdist_mac_options = {
    'iconfile': ICON
}

bdist_dmg_options = {
    'volume_label': NAME
}

setup(name = NAME,
      version = VER,
      description = 'A DICOM Sorting Utility',
      options = {
          "build": build_options,
          "bdist_exe": bdist_exe_options,
          "bdist_mac": bdist_mac_options,
          "bdist_dmg": bdist_dmg_options
      },
      executables=[exe])
