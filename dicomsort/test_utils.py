import os
import unittest

from pydicom.dataset import Dataset, FileDataset

from dicomsort import utils


class TestRecurvsiveReplaceTokens(unittest.TestCase):
    def test_no_tokens(self):
        formatString = 'no_token_string'
        output = utils.recursive_replace_tokens(formatString, {})

        assert output == formatString

    def test_non_nested_tokens(self):
        formatString = 'prefix_%(Key)s_suffix'
        values = {'Key': 'value'}
        output = utils.recursive_replace_tokens(formatString, values)

        assert output == 'prefix_value_suffix'

    def test_nested_tokens(self):
        formatString = 'prefix_%(Key1)s_suffix'
        values = {'Key1': '%(Key2)s', 'Key2': 'value'}
        output = utils.recursive_replace_tokens(formatString, values)

        assert output == 'prefix_value_suffix'

    def test_max_nested_tokens(self):
        formatString = 'prefix_%(Key1)s_suffix'
        # Make the values recurse
        values = {
            'Key1': '%(Key2)s',
            'Key2': '%(Key3)s',
            'Key3': '%(Key4)s',
            'Key4': '%(Key5)s',
            'Key5': '%(Key6)s',
            'Key6': 'blah',
        }

        # Will only perform replacements 5 times
        output = utils.recursive_replace_tokens(formatString, values)

        assert output == 'prefix_%(Key6)s_suffix'


class TestGrouper:
    def test_empty(self):
        output = utils.grouper([], 1)
        assert list(output) == []

    def test_equal_sizes(self):
        iterable = [1, 2, 3, 4, 5, 6]
        output = utils.grouper(iterable, 2)

        assert list(output) == [(1, 2), (3, 4), (5, 6)]

    def test_unequal_sizes(self):
        iterable = [1, 2, 3, 4, 5]
        output = utils.grouper(iterable, 2)

        assert list(output) == [(1, 2), (3, 4), (5, None)]


class TestIsDicom:
    def test_dicomdir(self, dicom_generator):
        dicomdir, _ = dicom_generator('DICOMDIR')

        assert utils.isdicom(dicomdir) is False

    def test_invalid_dicom(self, tmpdir):
        fobj = tmpdir.join('invalid')
        fobj.write('invalid')

        assert utils.isdicom(str(fobj)) is False

    def test_valid_dicom(self, dicom_generator):
        filename, _ = dicom_generator()

        assert utils.isdicom(filename) is not False


class TestCleanDirectoryName:
    def test_no_invalid_chars(self):
        dirname = 'clean'
        assert utils.clean_directory_name(dirname) == dirname

    def test_invalid_chars(self):
        dirname = 'prefix\\:*?|"<>suffix'
        assert utils.clean_directory_name(dirname) == 'prefix_suffix'


class TestCleanPath:
    def test_no_invalid_parts(self):
        path = os.path.join('/tmp/dir/ok')
        assert utils.clean_path(path) == path

    def test_with_invalid_parts(self):
        dirname = 'prefix:*?|"<>suffix'
        path = os.path.join('tmp', 'dir', dirname, dirname)
        expected = os.path.join('tmp', 'dir', 'prefix_suffix', 'prefix_suffix')
        assert utils.clean_path(path) ==  expected
