import pydicom
import pytest

from dicomsort.dicomsorter import Dicom


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

        dcm.SetAnonRules({'Field': lambda: 'Value'})

        assert dcm['Field'] == 'Value'

    def test_get_item_override_value(self, dicom_generator):
        filename, dicom = dicom_generator()
        dcm = Dicom(filename, dcm=dicom)

        dcm.SetAnonRules({'Field': 'Value'})

        assert dcm['Field'] == 'Value'

    def test_get_item_dicom_attribute(self, dicom_generator):
        filename, dicom = dicom_generator(PatientName='Suever')
        dcm = Dicom(filename, dcm=dicom)

        assert dcm['PatientName'] == 'Suever'

    def test_get_file_extension(self, dicom_generator):
        filename, _ = dicom_generator('image.ext')

        dcm = Dicom(filename)
        assert dcm._get_file_extension() == '.ext'

    def test_get_file_extension_empty(self, dicom_generator):
        filename, _ = dicom_generator('image')

        dcm = Dicom(filename)
        assert dcm._get_file_extension() == ''

    def test_get_series_description(self, dicom_generator):
        filename, dataset = dicom_generator(
            SeriesDescription=' My Series',
            SeriesNumber=1
        )

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_series_description() == 'My Series_Series0001'

    def test_get_series_description_no_description(self, dicom_generator):
        filename, dicom = dicom_generator(SeriesNumber=1)
        del dicom.SeriesDescription

        dcm = Dicom(filename, dcm=dicom)

        assert dcm._get_series_description() == 'Series0001'

    def test_get_series_description_series_first(self, dicom_generator):
        filename, dataset = dicom_generator(
            SeriesDescription='My Series',
            SeriesNumber=1
        )

        dcm = Dicom(filename, dcm=dataset)
        dcm.seriesFirst = True

        assert dcm._get_series_description() == 'Series0001_My Series'


    def test_get_patient_age_with_field(self, dicom_generator):
        age = '10Y'
        filename, dataset = dicom_generator(PatientAge=age)

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_patient_age() == age

    def test_get_patient_age_without_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator()

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_patient_age() == ''

    def test_get_patient_age_with_empty_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator(PatientBirthDate='')

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_patient_age() == ''

    def test_get_patient_age_with_birth_date(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientBirthDate='20180101',
            StudyDate='20190701'
        )

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_patient_age() == '001Y'

    def test_get_image_type_no_type(self, dicom_generator):
        filename, dataset = dicom_generator()

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == 'Unknown'

    def test_get_image_type_magnitude(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['FFE', 'M', 'JUNK'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == 'Mag'

    def test_get_image_type_generic(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['A', 'B'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == 'Image'

    def test_get_image_type_phase(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['P', 'BLAH'])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == 'Phase'

    def test_get_image_type_phoenix(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['CSA REPORT', ''])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == 'Phoenix'

    def test_get_image_type_3drecon(self, dicom_generator):
        filename, dataset = dicom_generator(ImageType=['CSA 3D EDITOR', ''])

        dcm = Dicom(filename, dcm=dataset)

        assert dcm._get_image_type() == '3DRecon'
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
        dcm.SetAnonRules({'PatientName': 'ANON'})

        assert dcm.is_anonymous() is True

    def test_anonymization_invalid_input(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        with pytest.raises(Exception) as excinfo:
            dcm.SetAnonRules('')

        assert excinfo.value.args[0] == 'Anon rules must be a dictionary'

    def test_anonymization(self, dicom_generator):
        filename, dataset = dicom_generator()
        dcm = Dicom(filename, dcm=dataset)

        adict = {'Key': 'Value'}

        dcm.SetAnonRules(adict)

        assert dcm.anondict == adict
        assert dcm.overrides['Key'] == 'Value'
        assert dcm['Key'] == 'Value'

    def test_anonymize_age(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientAge='030Y',
            PatientBirthDate='19890201',
            StudyDate='20190301'
        )

        dcm = Dicom(filename, dcm=dataset)

        dcm.SetAnonRules({'PatientBirthDate': ''})

        assert dcm['PatientAge'] == '030Y'
        assert dcm['PatientBirthDate'] == '19890101'

    def test_anonymize_birthdate(self, dicom_generator):
        date = '20191101'
        filename, dataset = dicom_generator(PatientBirthDate='20200101')
        dcm = Dicom(filename, dcm=dataset)

        dcm.SetAnonRules({'PatientBirthDate': date})

        assert dcm.overrides['PatientBirthDate'] == date
        assert dcm['PatientBirthDate'] == date

    def test_anonymize_empty_birthdate(self, dicom_generator):
        filename, dataset = dicom_generator(
            PatientBirthDate='20170601',
            StudyDate='20180201',
        )
        dcm = Dicom(filename, dcm=dataset)

        dcm.SetAnonRules({'PatientBirthDate': ''})

        # Maintains the patient age but uses January 01
        assert dcm.overrides['PatientBirthDate'] == '20180101'
        assert dcm['PatientBirthDate'] == '20180101'

        # 1-day Old
        dataset.PatientBirthDate = '20180131'

        dcm.SetAnonRules({'PatientBirthDate': ''})
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

        # Filename format which uses attributes that are not defined
        filename = '%(SeriesNumber)d file'

        dest = dcm.get_destination(root, directory, filename)

        expected = '/my/base/directory/UNKNOWN/desc_Series0001 name/1 file'
        assert dest == expected
