import collections
import os
import pydicom
import re
import sys
import shutil
import itertools

from dicomsort import gui
from threading import Thread
from pydicom.errors import InvalidDicomError


def recursive_replace_tokens(formatString, repobj):
    max_rep = 5
    rep = 0

    while re.search('%\(.*\)', formatString) and rep < max_rep:
        formatString = formatString % repobj
        rep = rep + 1

    return formatString


def grouper(iterable, n):
    return zip(* [iter(iterable), ] * n)


def clean_directory_name(path):
    badchars = '[\\/\:\*\?\"\<\>\|]+'
    return re.sub(badchars, '_', path)


def clean_path(path):
    badchars = '[\\/\:\*\?\"\<\>\|]+'

    outpath = ''

    head, tail = os.path.split(path)

    while tail:
        outpath = os.path.join(re.sub(badchars, '_', tail), outpath)
        head, tail = os.path.split(head)

    return os.path.join(head, outpath)[:-1]


def isdicom(filename):
    if os.path.basename(filename).lower() == 'dicomdir':
        return False
    try:
        return pydicom.read_file(filename)
    except InvalidDicomError:
        return False


class Dicom():
    def __init__(self, filename, dcm=None):
        """
        Takes a dicom filename in and returns instance that can be used to sort
        """
        # Be sure to do encoding because Windows sucks
        self.filename = filename.encode("UTF-8")

        # Load the DICOM object
        if dcm:
            self.dicom = dcm
        else:
            self.dicom = pydicom.read_file(self.filename)

        self.seriesFirst = False

        self.create_default_overrides()

        # Combine with anons - Empty but provides the option to have defaults
        # anondict = dict()
        # self.overrides = dict(self.default_overrides, **anondict)

    def __getitem__(self, attr):
        """
        Points the reference to the property unless an override is specified
        """
        try:
            item = self.overrides[attr]
            if isinstance(item, collections.Callable):
                return item()

            return item
        except KeyError:
            return getattr(self.dicom, attr)

    def create_default_overrides(self):
        # Specify which field-types to override
        self.default_overrides = {
            'ImageType': self._get_image_type,
            'FileExtension': self._get_file_extension,
            'SeriesDescription': self._get_series_description
        }

        self.overrides = dict(self.default_overrides)

    def _get_file_extension(self):
        filename, extension = os.path.splitext(self.dicom.filename)
        return extension

    def _get_series_description(self):
        if not hasattr(self.dicom, 'SeriesDescription'):
            out = 'Series%04d' % self.dicom.SeriesNumber
        else:
            if self.seriesFirst:
                out = 'Series%04d_%s' % (self.dicom.SeriesNumber,
                                         self.dicom.SeriesDescription)
            else:
                out = '%s_Series%04d' % (self.dicom.SeriesDescription,
                                         self.dicom.SeriesNumber)

        # Strip so we don't have any leading/trailing spaces
        return out.strip()

    def _get_patient_age(self):
        """
        Computes the age of the patient
        """
        if 'PatientAge' in self.dicom:
            age = self.dicom.PatientAge
        elif self.dicom.PatientBirthDate == '':
            age = ''
        else:
            age = (int(self.dicom.StudyDate) -
                   int(self.dicom.PatientBirthDate)) / 10000
            age = '%03dY' % age

        return age

    def _get_image_type(self):
        """
        Determines the human-readable type of the image
        """

        types = {
            'Phase': set(['P', ]),
            '3DRecon': set(['CSA 3D EDITOR', ]),
            'Phoenix': set(['CSA REPORT', ]),
            'Mag': set(['FFE', 'M'])
        }

        try:
            imType = set(self.dicom.ImageType)
        except AttributeError:
            return 'Unknown'

        for typeString, match in types.iteritems():
            if match.issubset(imType):
                if typeString == '3DRecon':
                    self.dicom.InstanceNumber = self.dicom.SeriesNumber

                return typeString

        return 'Image'

    def get_destination(self, root, dirFormat, fileFormat):

        # First we need to clean up the elements of dirFormat to make sure that
        # we don't have any bad characters (including /) in the folder names
        directory = root
        for item in dirFormat:
            try:
                subdir = recursive_replace_tokens(item, self)
                subdir = clean_directory_name(subdir)
            except AttributeError:
                subdir = 'UNKNOWN'

            directory = os.path.join(directory, subdir)

        # Maximum recursion is 5 so we don't end up with any infinite loop
        # situations
        try:
            filename = recursive_replace_tokens(fileFormat, self)
            filename = clean_path(filename)
            out = os.path.join(directory, filename)
        except AttributeError:
            # Now just use the initial filename
            origname = os.path.split(self.filename)[1]
            out = os.path.join(directory, origname)

        return out


    def SetAnonRules(self, anondict):
        # Appends the rules to the overrides so that we can alter them
        if isinstance(anondict, dict):
            self.anondict = anondict
        else:
            raise Exception('Anon rules must be a dictionary')

        if 'PatientBirthDate' in self.anondict:
            if self.anondict['PatientBirthDate'] != '' or self.dicom.PatientBirthDate == '':
                self.overrides = dict(self.default_overrides, **anondict)
                return

            # First we need to figure out how old they are
            if 'PatientAge' in self.dicom and 'StudyDate' in self.dicom:
                self.dicom.PatientAge = self._get_patient_age()

            if 'StudyDate' in self.dicom:
                # Now set it so it is just the birth year but make it so that
                # the proper age is returned when doing year math
                birthDate = int(self.dicom.PatientBirthDate[4:])
                studyDate = int(self.dicom.StudyDate[4:])

                # If the study was performed after their birthday this year
                if studyDate >= birthDate:
                    # Keep original birthyear
                    newBirth = '%s0101' % self.dicom.PatientBirthDate[:4]
                else:
                    byear = self.dicom.PatientBirthDate[:4]
                    newBirth = '%d0101' % (int(byear) + 1)

                self.anondict['PatientBirthDate'] = newBirth

        # Update the override dictionary
        self.overrides = dict(self.default_overrides, **anondict)

    def is_anonymous(self):
        return self.default_overrides != self.overrides

    def check_dir(self, dest):
        dest = os.path.dirname(dest)

        if sys.platform == "win32":
            exceptions = WindowsError
        else:
            exceptions = OSError

        try:
            os.makedirs(dest)
        except exceptions:
            return

    def sort(self, root, dirFields, fnameString, test=False, rootdir=None, keepOriginal=True):

        # If we want to sort in place
        if dirFields is None:
            destination = os.path.relpath(self.filename, rootdir[0])
            destination = os.path.join(root, destination)
        else:
            destination = self.get_destination(root, dirFields, fnameString)

        if test:
            print(destination)
            return

        self.check_dir(destination)

        # Check if destination exists
        while os.path.exists(destination):
            destination = destination + '.copy'

        if self.is_anonymous():
            # Actually write the anononymous data
            # write everything in anondict -> Parse it so we can have dynamic fields
            for key in self.anondict.keys():
                replacementvalue = self.anondict[key] % self
                try:
                    self.dicom.data_element(key).value = replacementvalue
                except KeyError:
                    continue

            self.dicom.save_as(destination)

            if keepOriginal == False:
                os.remove(self.filename)

        else:
            if keepOriginal == True:
                shutil.copy(self.filename, destination)
            else:
                shutil.move(self.filename, destination)


class Sorter(Thread):
    def __init__(self, files, outDir, dirFormat, fileFormat,
                 anon=dict(), keep_filename=False, iterator=None,
                 test=False, listener=None, total=None, root=None,
                 seriesFirst=False, keepOriginal=True):

        self.dirFormat = dirFormat
        self.fileFormat = fileFormat
        self.fileList = files
        self.anondict = anon
        self.keep_filename = keep_filename
        self.seriesFirst = seriesFirst
        self.keepOriginal = keepOriginal
        self.outDir = outDir
        self.test = test
        self.iter = iterator
        self.root = root

        if not isinstance(self.fileList, tuple):
            self.fileList = (self.fileList,)

        if total is None:
            self.total = len(self.fileList)
        else:
            self.total = total

        self.isgui = False

        if listener:
            self.listener = listener
            self.isgui = True

        Thread.__init__(self)
        self.start()

    def run(self):

        if self.isgui:
            import wx

        files = self.fileList

        for file in files:
            if not file:
                continue

            dcm = isdicom(file)
            if dcm:
                dcm = Dicom(file, dcm)
                dcm.SetAnonRules(self.anondict)
                dcm.seriesFirst = self.seriesFirst

                # Use the original filename for 3d recons
                if self.keep_filename:
                    filename = os.path.basename(file)
                else:
                    filename = self.fileFormat

                dcm.sort(self.outDir,
                         self.dirFormat,
                         filename,
                         test=self.test,
                         rootdir=self.root,
                         keepOriginal=self.keepOriginal)

            if self.iter:
                count = self.iter.next()
                if self.isgui:
                    event = gui.CounterEvent(Count=count, total=self.total)
                    wx.PostEvent(self.listener, event)


class DicomSorter():
    def __init__(self, pathname=None):
        # Use current directory by default
        if not pathname:
            pathname = [os.getcwd(), ]

        if not isinstance(pathname, list):
            pathname = [pathname, ]

        self.pathname = pathname

        self.folders = []
        self.filename = '%(ImageType)s (%(InstanceNumber)04d)%(FileExtension)s'

        self.sorters = list()

        # Don't anonymize by default
        self.anondict = dict()

        self.keep_filename = False
        self.seriesFirst = False
        self.keepOriginal = True

    def IsSorting(self):
        for sorter in self.sorters:
            if sorter.isAlive():
                return True

        return False

    def SetAnonRules(self, anondict):
        # Appends the rules to the overrides so that we can alter them
        if not isinstance(anondict, dict):
            raise Exception('Anon rules must be a dictionary')

        # Make sure to convert unicode to raw strings (pydicom bug)
        for key, value in anondict.items():
            anondict[key] = value.encode()

        self.anondict = anondict

    def GetFolderFormat(self):
        # Check to see if we are using the origin directory structure
        if self.folders is None:
            return None

        # Make a local copy
        folderList = self.folders[:]

        return folderList

    def Sort(self, outputDir, test=False, listener=None):
        # This should be moved to a worker thread

        dirFormat = self.GetFolderFormat()

        fileList = list()

        for path in self.pathname:
            for root, dir, files in os.walk(path):
                for file in files:
                    fileList.append(os.path.join(root, file))

        # Make sure that we don't have duplicates
        fileList = list(set(fileList))

        numberOfThreads = 2
        numberOfFiles = len(fileList)
        numberPerThread = int(round(float(numberOfFiles) / float(numberOfThreads)))

        fileGroups = grouper(fileList, numberPerThread)

        dirFormat = self.GetFolderFormat()

        self.sorters = list()

        iterator = itertools.count(1)

        for group in fileGroups:

            sorter = Sorter(group, outputDir, dirFormat, self.filename,
                            self.anondict, self.keep_filename,
                            iterator=iterator, test=test, listener=listener,
                            total=numberOfFiles, root=self.pathname,
                            seriesFirst=self.seriesFirst,
                            keepOriginal=self.keepOriginal)

            self.sorters.append(sorter)

    def GetAvailableFields(self):
        for path in self.pathname:
            for root, dirs, files in os.walk(path):
                for file in files:
                    filename = os.path.join(root, file)
                    dcm = isdicom(filename)
                    if dcm:
                        return dcm.dir('')

        msg = ''.join([';'.join(self.pathname), ' contains no DICOMs'])
        raise DicomFolderError(msg)


class DicomFolderError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
