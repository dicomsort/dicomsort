import collections
import itertools
import os
import pydicom
import shutil

from six import ensure_text
from six.moves import queue
from threading import Thread

from dicomsort import errors, utils
from dicomsort.gui import events


THREAD_COUNT = 2


class Dicom:
    def __init__(self, filename, dcm=None):
        """
        Takes a dicom filename in and returns instance that can be used to sort
        """
        # Be sure to do encoding because Windows sucks
        self.filename = ensure_text(filename)

        # Load the DICOM object
        if dcm:
            self.dicom = dcm
        else:
            self.dicom = pydicom.read_file(self.filename)

        self.series_first = False

        self.default_overrides = {
            'ImageType': self._image_type,
            'FileExtension': self._file_extension,
            'SeriesDescription': self._series_description
        }

        self.overrides = dict(self.default_overrides)

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

    def _file_extension(self):
        filename, extension = os.path.splitext(self.dicom.filename)
        return extension

    def _series_description(self):
        if not hasattr(self.dicom, 'SeriesDescription'):
            out = 'Series%04d' % self.dicom.SeriesNumber
        else:
            if self.series_first:
                out = 'Series%04d_%s' % (self.dicom.SeriesNumber,
                                         self.dicom.SeriesDescription)
            else:
                out = '%s_Series%04d' % (self.dicom.SeriesDescription,
                                         self.dicom.SeriesNumber)

        # Strip so we don't have any leading/trailing spaces
        return out.strip()

    def _patient_age(self):
        """
        Computes the age of the patient
        """
        if 'PatientAge' in self.dicom:
            age = self.dicom.PatientAge
        elif 'PatientBirthDate' not in self.dicom or \
                self.dicom.PatientBirthDate == '':
            age = ''
        else:
            age = (int(self.dicom.StudyDate) -
                   int(self.dicom.PatientBirthDate)) / 10000
            age = '%03dY' % age

        return age

    def _image_type(self):
        """
        Determines the human-readable type of the image
        """

        types = {
            'Phase': {'P', },
            '3DRecon': {'CSA 3D EDITOR', },
            'Phoenix': {'CSA REPORT', },
            'Mag': {'FFE', 'M'},
        }

        try:
            image_type = set(self.dicom.ImageType)
        except AttributeError:
            return 'Unknown'

        for typeString, match in types.items():
            if match.issubset(image_type):
                if typeString == '3DRecon':
                    self.dicom.InstanceNumber = self.dicom.SeriesNumber

                return typeString

        return 'Image'

    def get_destination(self, root, directory_format, filename_format):

        # First we need to clean up the elements of directory_format to make
        # sure that we don't have any bad characters (including /) in the
        # folder names
        directory = root
        for item in directory_format:
            try:
                subdir = utils.recursive_replace_tokens(item, self)
                subdir = utils.clean_directory_name(subdir)
            except AttributeError:
                subdir = 'UNKNOWN'

            directory = os.path.join(directory, subdir)

        # Maximum recursion is 5 so we don't end up with any infinite loop
        # situations
        try:
            filename = utils.recursive_replace_tokens(filename_format, self)
            filename = utils.clean_path(filename)
            out = os.path.join(directory, filename)
        except AttributeError:
            # Now just use the initial filename
            origname = os.path.split(self.filename)[1]
            out = os.path.join(directory, origname)

        return out

    def set_anonymization_rules(self, anonymization_lookup):
        # Appends the rules to the overrides so that we can alter them
        if isinstance(anonymization_lookup, dict):
            self.anonymization_lookup = anonymization_lookup
        else:
            raise Exception('Anon rules must be a dictionary')

        if 'PatientBirthDate' in self.anonymization_lookup:
            if self.anonymization_lookup['PatientBirthDate'] != '' or \
                    self.dicom.PatientBirthDate == '':

                self.overrides = dict(
                    self.default_overrides,
                    **anonymization_lookup
                )

                return

            # First we need to figure out how old they are
            if 'PatientAge' in self.dicom and 'StudyDate' in self.dicom:
                self.dicom.PatientAge = self._patient_age()

            if 'StudyDate' in self.dicom:
                # Now set it so it is just the birth year but make it so that
                # the proper age is returned when doing year math
                birth_date = int(self.dicom.PatientBirthDate[4:])
                study_date = int(self.dicom.StudyDate[4:])

                # If the study was performed after their birthday this year
                if study_date >= birth_date:
                    new_birth_date = '%s0101' % self.dicom.PatientBirthDate[:4]
                else:
                    birth_year = self.dicom.PatientBirthDate[:4]
                    new_birth_date = '%d0101' % (int(birth_year) + 1)

                self.anonymization_lookup['PatientBirthDate'] = new_birth_date

        # Update the override dictionary
        self.overrides = dict(self.default_overrides, **anonymization_lookup)

    def is_anonymous(self):
        return self.default_overrides != self.overrides

    def sort(self, root, directory_fields, filename_string, test=False,
             rootdir=None, keep_original=True):

        # If we want to sort in place
        if directory_fields is None:
            destination = os.path.relpath(self.filename, rootdir[0])
            destination = os.path.join(root, destination)
        else:
            destination = self.get_destination(
                root, directory_fields, filename_string
            )

        if test:
            print(destination)
            return

        utils.mkdir(os.path.dirname(destination))

        # Check if destination exists
        while os.path.exists(destination):
            destination = destination + '.copy'

        if self.is_anonymous():
            # Actually write the anonymous data
            # write everything in anonymization_lookup -> Parse it so we can
            # have dynamic fields
            for key in self.anonymization_lookup.keys():
                replacement_value = self.anonymization_lookup[key] % self
                try:
                    self.dicom.data_element(key).value = replacement_value
                except KeyError:
                    continue

            self.dicom.save_as(destination)

            if keep_original is False:
                os.remove(self.filename)

        else:
            if keep_original:
                shutil.copy(self.filename, destination)
            else:
                shutil.move(self.filename, destination)


class Sorter(Thread):
    def __init__(self, queue, output_directory, directory_format,
                 filename_format, lookup=None, keep_filename=False,
                 iterator=None, test=False, listener=None, total=None,
                 root=None, series_first=False, keep_original=True):

        self.directory_format = directory_format
        self.filename_format = filename_format
        self.queue = queue
        self.anonymization_lookup = lookup or dict()
        self.keep_filename = keep_filename
        self.series_first = series_first
        self.keep_original = keep_original
        self.output_directory = output_directory
        self.test = test
        self.iter = iterator
        self.root = root
        self.total = total or self.queue.qsize()

        self.is_gui = False

        if listener:
            self.listener = listener
            self.is_gui = True

        Thread.__init__(self)
        self.start()

    def sort_image(self, filename):
        dcm = utils.isdicom(filename)

        if not dcm:
            return

        dcm = Dicom(filename, dcm)
        dcm.set_anonymization_rules(self.anonymization_lookup)
        dcm.series_first = self.series_first

        # Use the original filename for 3d recons
        if self.keep_filename:
            output_filename = os.path.basename(filename)
        else:
            output_filename = self.filename_format

        dcm.sort(
            self.output_directory,
            self.directory_format,
            output_filename,
            test=self.test,
            rootdir=self.root,
            keep_original=self.keep_original
        )

    def increment_counter(self):
        if self.iter is None:
            return

        count = next(self.iter)

        if self.is_gui is False:
            return

        event = events.CounterEvent(Count=count, total=self.total)
        events.post_event(self.listener, event)

    def run(self):
        while True:
            try:
                filename = self.queue.get_nowait()
                self.sort_image(filename)
                self.increment_counter()
            # TODO: Rescue any other errors and quarantine the files
            except queue.Empty:
                return


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

        self.queue = queue.Queue()

        self.sorters = list()

        # Don't anonymize by default
        self.anonymization_lookup = dict()

        self.keep_filename = False
        self.series_first = False
        self.keep_original = True

    def is_sorting(self):
        for sorter in self.sorters:
            if sorter.isAlive():
                return True

        return False

    def set_anonymization_rules(self, anonymization_lookup):
        # Appends the rules to the overrides so that we can alter them
        if not isinstance(anonymization_lookup, dict):
            raise Exception('Anon rules must be a dictionary')

        self.anonymization_lookup = anonymization_lookup

    def folder_format(self):
        # Check to see if we are using the origin directory structure
        if self.folders is None:
            return None

        # Make a local copy
        folder_list = self.folders[:]

        return folder_list

    def sort(self, output_directory, test=False, listener=None):
        # This should be moved to a worker thread
        for path in self.pathname:
            for root, _, files in os.walk(path):
                for filename in files:
                    self.queue.put(os.path.join(root, filename))

        number_of_files = self.queue.qsize()
        dir_format = self.folder_format()

        self.sorters = list()

        iterator = itertools.count(1)

        for _ in range(min(THREAD_COUNT, number_of_files)):
            sorter = Sorter(
                self.queue, output_directory, dir_format, self.filename,
                self.anonymization_lookup, self.keep_filename,
                iterator=iterator, test=test, listener=listener,
                total=number_of_files, root=self.pathname,
                series_first=self.series_first,
                keep_original=self.keep_original
            )

            self.sorters.append(sorter)

    def available_fields(self):
        for path in self.pathname:
            for root, dirs, files in os.walk(path):
                for filename in files:
                    dcm = utils.isdicom(os.path.join(root, filename))
                    if dcm:
                        return dcm.dir('')

        msg = ''.join([';'.join(self.pathname), ' contains no DICOMs'])
        raise errors.DicomFolderError(msg)
