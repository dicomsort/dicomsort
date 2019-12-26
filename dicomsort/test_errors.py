import unittest

from dicomsort.errors import DicomFolderError


class TestDicomFolderError(unittest.TestCase):
    def test_constructor(self):
        baseError = Exception('OH NO')
        err = DicomFolderError(baseError)

        assert isinstance(err, DicomFolderError)
        assert isinstance(err, Exception)

    def test_string_representation(self):
        baseError = Exception('OH NO')
        err = DicomFolderError(baseError)

        assert str(err) == repr(baseError)
