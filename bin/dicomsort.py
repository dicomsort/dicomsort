#!/usr/bin/env python
from __future__ import absolute_import

import os
import sys

current = os.path.realpath(os.path.dirname(__file__))
parent = os.path.realpath(os.path.join(current, '..'))

sys.path.insert(0, parent)

from dicomsort.gui.core import DicomSort


def main():
    ds = DicomSort(0)
    ds.MainLoop()


if __name__ == '__main__':
    main()
