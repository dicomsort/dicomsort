import dicomsort
import os
import sys

from setuptools import find_packages, setup

NAME = 'dicomsort'
AUTHOR = 'Jonathan Suever'
AUTHOR_EMAIL = 'suever@gmail.com'
MAINTAINER = AUTHOR
MAINTAINER_EMAIL = AUTHOR_EMAIL
DESCRIPTION = 'A DICOM Sorting Utility'
URL = 'https://dicomsort.com'
DOWNLOAD_URL = 'http://dicomsort.com/downloads.html'
LICENSE = 'MIT'
VERSION = dicomsort.__version__

# Retrieve long description from README.md
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(BASE_PATH, 'README.md')) as f:
    LONG_DESCRIPTION = f.read()

ICON_DIR = 'icons'
ICO_FILE = os.path.join(ICON_DIR, 'DSicon.ico')
ICNS_FILE = os.path.join(ICON_DIR, 'DSicon.icns')

CLASSIFIERS = [
    "License :: OSI Approved :: MIT License",
    "Intended Audience :: Developers",
    "Intended Audience :: Healthcare Industry",
    "Intended Audience :: Science/Research",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.4",
    "Programming Language :: Python :: 3.5",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 3.7",
    "Operating System :: OS Independent",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Topic :: Scientific/Engineering :: Physics",
    "Topic :: Software Development :: Libraries"
]

KEYWORDS = "dicom sorting images"

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
         type,         # Shortcut
         directory,    # Directory_
         name,         # Name
         'TARGETDIR',  # Component_
         target,       # Target
         None,         # Arguments
         None,         # Description
         None,         # Hotkey
         None,         # Icon
         None,         # IconIndex
         None,         # ShowCmd
         'TARGETDIR'   # WkDir
     )


if __name__ == '__main__':
    setup(
        name=NAME,
        version=VERSION,
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        author=AUTHOR,
        author_email=AUTHOR_EMAIL,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type='text/markdown',
        url=URL,
        download_url=DOWNLOAD_URL,
        license=LICENSE,
        keywords=KEYWORDS,
        classifiers=CLASSIFIERS,
        packages=find_packages(),
        install_requires=[
            'configobj',
            'pydicom',
            'wxpython',
        ],
        zip_safe=False,
        scripts=[
            os.path.join('bin', 'dicomsort')
        ],
    )
