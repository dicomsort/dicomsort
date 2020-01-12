import os
import pydicom
import pytest
import time

from six.moves.queue import Queue

from dicomsort.dicomsorter import Dicom, DicomSorter, Sorter
from dicomsort.errors import DicomFolderError


def default_sorter():
    return Sorter(Queue(), '', [], '')


class TestDicom:
    def test_constructor_without_dicom(self, dicom_generator, mocker):
        func = mocker.patch.object(pydicom, 'read_file', return_value='dicom')

        filename, _ = dicom_generator()
        dcm = Dicom(filename)

        func.assert_called_once_with(filename)
        assert dcm.dicom == 'dicom'

    def test_constructor_with_dicom(self, dicom_generator, mocker):
        func = mocker.patch.object(pydicom, 'read_file', return_value='dicom')

        filename, dataset = dicom_generator()

        dcm = Dicom(filename, dcm=dataset)

        func.assert_not_called()
        assert dcm.dicom == dataset

    def test_get_item_override_function(self, dicom_generator):
        filename, dicom = dicom_generator()
        dcm = Dicom(filename, dcm=dicom)

        dcm.set_anonymization_rules({'Field': lambda: 'Value'})

        assert dcm['Field'] == 'Value'

    def test_get_item_override_value(self, dicom_generator):
        filename, dicom = dicom_generator()
        dcm = Dicom(filename, dcm=dicom)

        dcm.set_anonymization_rules({'Field': 'Value'})

        assert dcm['Field'] == 'Value'

    def test_get_item_dicom_attribute(self, dicom_generator):
        filename, dicom = dicom_generator(PatientName='Suever')
        dcm = Dicom(filename, dcm=dicom)

        assert dcm['PatientName'] == 'Suever'

    def test_get_file_extension(self, dicom_generator):
        filename, _ = dicom_generator('image.ext')

        dcm = Dicom(filename)
        assert dcm._file_extension() == '.ext'

    def test_get_file_extension_empty(self, dicom_generator):
        filename, _ = dicom_generator('image')

        dcm = Dicom(filename)
        assert dcm._file_extension() == ''

    def test_get_series_description(self, dicom_generator):
        filename, dataset = dicom_generator(
            SeriesDescription=' My Series',
            SeriesNumber=1
        )

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._series_description() == 'My Series_Series0001'

    def test_get_series_description_no_description(self, dicom_generator):
        filename, dicom = dicom_generator(SeriesNumber=1)
        del dicom.SeriesDescription

        dcm = Dicom(filename, dcm=dicom)

        assert dcm._series_description() == 'Series0001'

    def test_get_series_description_series_first(self, dicom_generator):
        filename, dataset = dicom_generator(
            SeriesDescription='My Series',
            SeriesNumber=1
        )

        dcm = Dicom(filename, dcm=dataset)
        dcm.series_first = True

        assert dcm._series_description() == 'Series0001_My Series'


    def test_get_patient_age_with_field(self, dicom_generator):
        age = '10Y'
        filename, dataset = dicom_generator(PatientAge=age)

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._patient_age() == age

    def test_get_patient_age_without_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator()

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._patient_age() == ''

    def test_get_patient_age_with_empty_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator(PatientBirthDate='')

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._patient_age() == ''

    def test_get_patient_age_with_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientBirthDate='20180101',
            StudyDate='20190701'
        )

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._patient_age() == '001Y'

    def test_get_image_type_no_type(self, dicom_generator):
        filename, dataset = dicom_generator()

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == 'Unknown'

    def test_get_image_type_magnitude(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['FFE', 'M', 'JUNK'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == 'Mag'

    def test_get_image_type_generic(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['A', 'B'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == 'Image'

    def test_get_image_type_phase(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['P', 'BLAH'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == 'Phase'

    def test_get_image_type_phoenix(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['CSA REPORT', ''])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == 'Phoenix'

    def test_get_image_type_3drecon(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['CSA 3D EDITOR', ''])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._image_type() == '3DRecon'
        assert dataset.InstanceNumber == dataset.SeriesNumber

    def test_create_default_overrides(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        assert 'ImageType' in dcm.default_overrides
        assert 'FileExtension' in dcm.default_overrides
        assert 'SeriesDescription' in dcm.default_overrides

        assert dcm.overrides == dcm.default_overrides

    def test_is_anonymous(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        assert dcm.is_anonymous() is False

        # Set anonimization rules
        dcm.set_anonymization_rules({'PatientName': 'ANON'})

        assert dcm.is_anonymous() is True

    def test_anonymization_invalid_input(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        with pytest.raises(Exception) as excinfo:
            dcm.set_anonymization_rules('')

        assert excinfo.value.args[0] == 'Anon rules must be a dictionary'

    def test_anonymization(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        adict = {'Key': 'Value'}

        dcm.set_anonymization_rules(adict)

        assert dcm.anonymization_lookup == adict
        assert dcm.overrides['Key'] == 'Value'
        assert dcm['Key'] == 'Value'

    def test_anonymize_age(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientAge='030Y',
            PatientBirthDate='19890201',
            StudyDate='20190301'
        )

        dcm = Dicom(filename, dcm=dataset)

        dcm.set_anonymization_rules({'PatientBirthDate': ''})

        assert dcm['PatientAge'] == '030Y'
        assert dcm['PatientBirthDate'] == '19890101'

    def test_anonymize_birthdate(self, dicom_generator):
        date = '20191101'
        filename, dataset = dicom_generator(PatientBirthDate='20200101')
        dcm = Dicom(filename, dcm=dataset)

        dcm.set_anonymization_rules({'PatientBirthDate': date})

        assert dcm.overrides['PatientBirthDate'] == date
        assert dcm['PatientBirthDate'] == date

    def test_anonymize_empty_birthdate(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientBirthDate='20170601',
            StudyDate='20180201',
        )
        dcm = Dicom(filename, dcm=dataset)

        dcm.set_anonymization_rules({'PatientBirthDate': ''})

        # Maintains the patient age but uses January 01
        assert dcm.overrides['PatientBirthDate'] == '20180101'
        assert dcm['PatientBirthDate'] == '20180101'

        # 1-day Old
        dataset.PatientBirthDate = '20180131'

        dcm.set_anonymization_rules({'PatientBirthDate': ''})
        assert dcm.overrides['PatientBirthDate'] == '20180101'
        assert dcm['PatientBirthDate'] == '20180101'

    def test_get_destination(self, dicom_generator):
        filename, dicom = dicom_generator(
            PatientName='name',
            SeriesDescription='desc',
            SeriesNumber=1,
        )

        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = '/my/base/directory'

        # Sub-directories
        directory = [
            '%(ImageType)s',
            '%(SeriesDescription)s %(PatientName)s'
        ]

        # Filename format
        filename = '%(SeriesNumber)d file'

        dest = dcm.get_destination(root, directory, filename)

        expected = '/my/base/directory/Unknown/desc_Series0001 name/1 file'
        assert dest == expected

    def test_get_destination_bad_filename_attr(self, dicom_generator):
        filename, dicom = dicom_generator(
            'image.dcm',
            PatientName='name',
            SeriesDescription='desc',
            SeriesNumber=1,
        )

        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = '/my/base/directory'

        # Sub-directories
        directory = [
            '%(ImageType)s',
            '%(SeriesDescription)s %(PatientName)s'
        ]

        # Filename format which uses attributes that are not defined
        filename = '%(Invalid)d file'

        dest = dcm.get_destination(root, directory, filename)
        expected = '/my/base/directory/Unknown/desc_Series0001 name/image.dcm'

        assert dest == expected

    def test_get_destination_bad_directory_attr(self, dicom_generator):
        filename, dicom = dicom_generator(
            'image.dcm',
            PatientName='name',
            SeriesDescription='desc',
            SeriesNumber=1,
        )

        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = '/my/base/directory'

        # Sub-directories
        directory = [
            '%(Invalid)s',  # Invalid attribute
            '%(SeriesDescription)s %(PatientName)s'
        ]

        # Filename format
        filename = '%(SeriesNumber)d file'

        dest = dcm.get_destination(root, directory, filename)

        expected = '/my/base/directory/UNKNOWN/desc_Series0001 name/1 file'
        assert dest == expected

    def test_sort_inplace(self, dicom_generator, tmpdir):
        filename, dicom = dicom_generator(
            'image.dcm',
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = None

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(
            root, directory, file_format,
            rootdir=[os.path.dirname(filename)],
        )

        destination = str(tmpdir.join('image.dcm'))

        assert os.path.exists(destination)

    def test_sort_keep_original(self, dicom_generator, tmpdir):
        filename, dicom = dicom_generator(
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = [
            '%(SeriesDescription)s',
            '%(SeriesDescription)s',
        ]

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(root, directory, file_format, keep_original=True)

        destination = tmpdir.join('desc_Series0001').join('desc_Series0001')
        destination = destination.join('Unknown')

        assert os.path.exists(filename)
        assert os.path.exists(str(destination))

    def test_sort_discard_original(self, dicom_generator, tmpdir):
        filename, dicom = dicom_generator(
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = [
            '%(SeriesDescription)s',
            '%(SeriesDescription)s',
        ]

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(root, directory, file_format, keep_original=False)

        destination = tmpdir.join('desc_Series0001').join('desc_Series0001')
        destination = destination.join('Unknown')

        assert os.path.exists(filename) is False
        assert os.path.exists(str(destination))

    def test_sort_anonymize(self, dicom_generator, tmpdir):
        filename, dicom = dicom_generator(
            PatientName='TO^BE^REMOVED',
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Overwrite the PatientName
        dcm.set_anonymization_rules({'PatientName': 'ANON'})

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = [
            '%(PatientName)s',
            '%(SeriesDescription)s',
        ]

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(root, directory, file_format, keep_original=False)

        destination = tmpdir.join('ANON').join('desc_Series0001')
        destination = str(destination.join('Unknown'))

        assert os.path.exists(destination)

        # Ensure the DICOM was modified
        newdcm = pydicom.read_file(destination)

        assert newdcm.PatientName == 'ANON'

    def test_sort_anonymize_invalid_field(self, dicom_generator, tmpdir):
        filename, dicom = dicom_generator(
            PatientName='TO^BE^REMOVED',
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Overwrite the PatientID (this field does not exist)
        dcm.set_anonymization_rules({'PatientID': 'ANON'})

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = [
            '%(PatientID)s',
            '%(SeriesDescription)s',
        ]

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(root, directory, file_format, keep_original=False)

        destination = tmpdir.join('ANON').join('desc_Series0001')
        destination = str(destination.join('Unknown'))

        assert os.path.exists(destination)

        # Make sure the field was not added to the new DICOM
        newdcm = pydicom.read_file(destination)

        assert 'PatientID' not in newdcm

    def test_sort_test(self, dicom_generator, tmpdir, capsys):
        filename, dicom = dicom_generator(
            SeriesDescription='desc',
            SeriesNumber=1,
        )
        dcm = Dicom(filename, dcm=dicom)

        # Base Directory
        root = str(tmpdir)

        # Subdirectories
        directory = [
            '%(SeriesDescription)s',
            '%(SeriesDescription)s',
        ]

        # Filename format
        file_format = '%(ImageType)s'

        dcm.sort(root, directory, file_format, keep_original=False, test=True)

        destination = tmpdir.join('desc_Series0001').join('desc_Series0001')
        destination = destination.join('Unknown')

        # The original is unmodified
        assert os.path.exists(filename)

        # The file was not actually copied
        assert os.path.exists(str(destination)) is False

        captured = capsys.readouterr()
        assert captured.out == str(destination) + '\n'


class TestDicomSorter:
    def test_constructor_defaults(self):
        sorter = DicomSorter()

        assert sorter.pathname == [os.getcwd(), ]

        # Booleans
        assert sorter.keep_filename is False
        assert sorter.series_first is False
        assert sorter.keep_original is True

        assert sorter.sorters == []
        assert sorter.folders == []
        assert sorter.anonymization_lookup == dict()

    def test_constructor_single_path(self):
        path = '/path'
        sorter = DicomSorter(path)

        assert sorter.pathname == [path, ]

    def test_constructor_multiple_paths(self):
        paths = ['/path1', '/path2']
        sorter = DicomSorter(paths)

        assert sorter.pathname == paths

    def test_get_available_fields_no_dicoms(self, tmpdir):
        fobj = tmpdir.join('tmp')
        fobj.write('invalid')

        root = str(tmpdir)

        sorter = DicomSorter(root)

        with pytest.raises(DicomFolderError):
            sorter.available_fields()

    def test_get_available_fields(self, dicom_generator):
        filename, dicom = dicom_generator()
        expected = dicom.dir('')

        root = os.path.dirname(filename)

        sorter = DicomSorter(root)

        assert sorter.available_fields() == expected

    def test_is_sorting_no_sorters(self):
        sorter = DicomSorter()

        assert sorter.sorters == []
        assert sorter.is_sorting() is False

    def test_is_sorting_active_sorters(self, mocker):
        sorter = DicomSorter()

        patch = mocker.patch.object(Sorter, 'isAlive')
        patch.return_value = True

        # Generate some sorters
        sorter.sorters.append(default_sorter())
        sorter.sorters.append(default_sorter())

        assert sorter.is_sorting() is True

    def test_is_sorting_inactive_sorters(self, mocker):
        sorter = DicomSorter()

        patch = mocker.patch.object(Sorter, 'isAlive')
        patch.return_value = False

        # Generate some sorters
        sorter.sorters.append(default_sorter())
        sorter.sorters.append(default_sorter())

        assert sorter.is_sorting() is False

    def test_get_folder_format_no_folders(self):
        sorter = DicomSorter()
        sorter.folders = None

        assert sorter.folder_format() is None

    def test_get_folder_format(self):
        sorter = DicomSorter()
        original = ['1', '2', '3']
        sorter.folders = original

        copy = sorter.folder_format()

        assert copy == original

        # modify the original to ensure it is a different object
        original.append('4')

        assert copy != original

    def test_set_anon_rules(self):
        sorter = DicomSorter()

        replacements = {
            'Key1': 'Value1',
            'Key2': 'Value2',
        }

        sorter.set_anonymization_rules(replacements)
        assert sorter.anonymization_lookup == replacements

    def test_set_anon_rules_invalid(self):
        sorter = DicomSorter()

        with pytest.raises(Exception) as exc_info:
            sorter.set_anonymization_rules('')

        assert exc_info.value.args[0] == 'Anon rules must be a dictionary'

    def test_sort(self, dicom_generator, mocker, tmpdir):
        filename, _ = dicom_generator(
            SeriesDescription='desc',
            SeriesNumber=1,
            InstanceNumber=1
        )

        sorter = DicomSorter()
        sorter.pathname = [os.path.dirname(filename), ]
        sorter.folders = [
            '%(SeriesDescription)s'
        ]

        output = tmpdir.join('output')

        sorter.sort(str(output))

        # Wait for sorting to complete
        while sorter.is_sorting():
            time.sleep(0.1)

        assert len(sorter.sorters) == 1

        series_folders = output.listdir()
        assert len(series_folders) == 1

        series_folder = series_folders[0]
        assert os.path.basename(str(series_folder)) == 'desc_Series0001'

        images = series_folder.listdir()
        assert len(images) == 1
        assert os.path.basename(str(images[0])) == 'Unknown (0001).dcm'
