import os
import pydicom
import re
import sys

from pydicom.errors import InvalidDicomError

INVALID_FILENAME_CHARS = re.compile('[\\\\/\\:\\*\\?\\"\\<\\>\\|]+')

if sys.platform == 'win32':
    DIRECTORY_EXISTS_EXCEPTION = WindowsError
else:
    DIRECTORY_EXISTS_EXCEPTION = OSError


def mkdir(directory):
    try:
        os.makedirs(directory)
    except DIRECTORY_EXISTS_EXCEPTION:
        return


def recursive_replace_tokens(formatString, repobj):
    max_rep = 5
    rep = 0

    while re.search('%\\(.*\\)', formatString) and rep < max_rep:
        formatString = formatString % repobj
        rep = rep + 1

    return formatString


def clean_directory_name(path):
    return re.sub(INVALID_FILENAME_CHARS, '_', path)


def clean_path(path):
    outpath = ''

    head, tail = os.path.split(path)

    while tail:
        outpath = os.path.join(clean_directory_name(tail), outpath)
        head, tail = os.path.split(head)

    return os.path.join(head, outpath)[:-1]


def isdicom(filename):
    if os.path.basename(filename).lower() == 'dicomdir':
        return False
    try:
        return pydicom.read_file(filename)
    except InvalidDicomError:
        return False
