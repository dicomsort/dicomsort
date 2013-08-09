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
URL = 'http://www.suever.net/software/dicomSort'

if sys.platform == 'darwin':
    OUTDIR = os.path.join('dist',NAME)
else:
    OUTDIR = os.path.join('dist', ''.join([NAME, ' ', VER]))

build_exe_options = {
    "include_msvcr": True,
    "icon":ICON,
    "include_files": includefiles
            }

exe = Executable(
    script='DicomSort.pyw',
    base=base,
    targetName=EXE,
    icon=ICON)

bdist_mac_options = {'iconfile':ICON}
bdist_dmg_options = {'volume_label':'DICOM Sort'}
#"iconfile": 'DSicon.icns'}

setup(name = NAME,
      version = VER,
      description = 'A DICOM Sorting Utility',
      options = {"build_exe": build_exe_options,
                 "bdist_mac": bdist_mac_options,
                 "bdist_dmg": bdist_dmg_options},
      executables=[exe])

if sys.platform == 'win32':

    INSTALLER = '%s_%s.setup' % (EXE.replace('.exe', ''), VER.replace('.', '_'))
    INSTALLER = INSTALLER.replace(' ', '_')

    # Construct the configuration string for Inno Setup
    innoDict = {'AppId': ID,
                'AppName': NAME,
                'AppVerName': '%s %s' % (NAME, VER),
                'AppPublisher': 'Jonathan Suever',
                'AppPublisherURL': URL,
                'AppSupportURL': URL,
                'AppUpdatesURL': URL,
                'DefaultDirName': '{pf}\%s' % NAME,
                'DefaultGroupName': NAME,
                'OutputDir': 'dist',
                'OutputBaseFilename': INSTALLER,
                'Compression': 'lzma',
                'SolidCompression': 'yes'}

    innoinput = '[Setup]\n'

    for key, value in innoDict.items():
        innoinput = ''.join([innoinput, '%s=%s\n' % (key, value)])

    lang = '[Languages]\nName: "english"; MessagesFile: "compiler:Default.isl"\n'
    task = '[Tasks]\nName:"desktopicon"; Description: "{cm:CreateDesktopIcon}";GroupDescription:"{cm:AdditionalIcons}";\n'

    OUTEXE = os.path.join(OUTDIR, EXE)
    INCLUDES = os.path.join(OUTDIR, '*')

    files = '''[Files]
    Source: "%s"; DestDir: "{app}"; Flags: ignoreversion
    Source: "%s"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs'''

    files = files % (OUTEXE, INCLUDES)

    ICONFILE = ICON

    icons = '''[Icons]
    Name: "{group}\%s"; Filename: "{app}\%s"; IconFilename: {app}\%s; IconIndex: 0; WorkingDir: "{app}"
    Name: "{userdesktop}\%s"; Filename: "{app}\%s"; Tasks: desktopicon; IconFilename: {app}\%s; IconIndex: 0'''

    icons = icons % (NAME, EXE, ICONFILE, NAME, EXE, ICONFILE)

    run = '''[Run]
    Filename: "{app}\%s"; Description: "{cm:LaunchProgram,%s}"; Flags: nowait postinstall skipifsilent'''

    run = run % (EXE, NAME)

    fullfile = '\n'.join([innoinput, lang, task, files, icons, run])

    # Write configuration to a temporary file
    f = open('wizard.iss', 'w')
    f.write(fullfile)
    f.close()

    print('Now Compiling using Inno Setup 5.')
    print('Be sure that it is installed, and added to your system PATH')
    os.system('Compil32 /cc wizard.iss')
    os.remove('wizard.iss')

print('Successfully created application and installer!')
