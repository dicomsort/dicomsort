import pydicom

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

