import os
import pydicom
import re

from pydicom.errors import InvalidDicomError

INVALID_FILENAME_CHARS = re.compile('[\\\\/\\:\\*\\?\\"\\<\\>\\|]+')


def recursive_replace_tokens(formatString, repobj):
    max_rep = 5
    rep = 0

    while re.search('%\\(.*\\)', formatString) and rep < max_rep:
        formatString = formatString % repobj
        rep = rep + 1

    return formatString


def grouper(iterable, n):
    return map(None, * [iter(iterable), ] * n)


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
