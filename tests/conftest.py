import pytest

from pydicom.dataset import Dataset, FileDataset


@pytest.fixture(scope='function')
def dicom_generator(tmpdir):
    def _dicom(filename='image.dcm', **values):
        filename = str(tmpdir.join(filename))

        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
        file_meta.MediaStorageSOPInstanceUID = '1.2.3'
        file_meta.ImplementationClassUID = '1.2.3.4'

        ds = FileDataset(filename, {}, file_meta=file_meta, preamble=b'\0'*128)
        ds.is_little_endian = True
        ds.is_implicit_VR = False

        ds.PatientName = 'Jonathan^Suever'
        ds.SeriesDescription = 'Dicom Sort Test Series'
        ds.SeriesNumber = 1

        ds.update(values)

        ds.save_as(filename)

        return filename, ds

    return _dicom
