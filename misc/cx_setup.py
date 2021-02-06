import os
import sys

from setuptools import find_packages
from cx_Freeze import setup, Executable

current = os.path.realpath(os.path.dirname(__file__))
parent = os.path.realpath(os.path.join(current, '..'))

sys.path.insert(0, parent)

from dicomsort import Metadata as meta  # noqa: E402

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DIST_DIR = os.path.join(BASE_PATH, 'dist')


class MacConfiguration:
    base = None
    executable_name = meta.pretty_name + '.app'
    icons = os.path.join(BASE_PATH, 'icons', 'DSicon.icns')
    output = os.path.join(DIST_DIR, meta.pretty_name)


class WindowsConfiguration:
    base = 'Win32GUI'
    executable_name = meta.pretty_name + '.exe'
    icons = os.path.join(BASE_PATH, 'icons', 'DSicon.ico')
    output = os.path.join(DIST_DIR, ' '.join([meta.pretty_name, meta.version]))


if sys.platform == 'darwin':
    config = MacConfiguration
else:
    config = WindowsConfiguration
    meta.name = meta.pretty_name


EXCLUDED_MODULES = [
    'numpy',
    'PIL',
    'pillow',
    'test',
    'tkinter',
]


def shortcut(type, directory):
    target = "[TARGETDIR]{}".format(config.executable_name)

    return (
         type,              # Shortcut
         directory,         # Directory_
         meta.pretty_name,  # Name
         'TARGETDIR',       # Component_
         target,            # Target
         None,              # Arguments
         None,              # Description
         None,              # Hotkey
         config.icons,      # Icon
         None,              # IconIndex
         None,              # ShowCmd
         'TARGETDIR'        # WkDir
     )


def start_menu_shortcut():
    return shortcut('ApplicationStartMenuShortcut', 'StartMenuFolder')


def desktop_shortcut():
    return shortcut('DesktopShortcut', 'DesktopFolder')


ENTRY_POINTS = {
   'console_scripts': [
       'dicomsort = dicomsort.gui:main',
   ],
}

executable = Executable(
    script=os.path.join('bin', 'dicomsort.py'),
    base=config.base,
    icon=config.icons,
    target_name=meta.pretty_name,
    shortcut_name=meta.pretty_name,
    copyright=meta.copyright
)


if __name__ == '__main__':
    setup(
        **meta.to_dict(),
        packages=find_packages(),
        options={
          'build': {
              'build_exe': config.output,
          },
          'build_exe': {
              'excludes': EXCLUDED_MODULES,
          },
          'bdist_msi': {
              'data': {
                  'Shortcut': [
                      desktop_shortcut(),
                      start_menu_shortcut(),
                  ],
              },
              'install_icon': config.icons,
              'summary_data': {
                  'author': meta.author,
                  'comments': meta.description,
                  'keywords': ' '.join(meta.keywords),
              },
              'target_name': '-'.join([meta.pretty_name, meta.version]),
          },
          'bdist_exe': {
              'include_msvcr': True,
              'include_files': [WindowsConfiguration.icons, ],
          },
          'bdist_mac': {
              'bundle_name': meta.pretty_name,
              'iconfile': MacConfiguration.icons
          },
          'bdist_dmg': {
              'volume_label': '-'.join([meta.name, meta.version])
          }
        },
        executables=[
            executable,
        ],
    )
