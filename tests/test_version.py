import unittest

import dicomsort


class TestVersion(unittest.TestCase):
    def test_version_string(self):
        assert dicomsort.__version__ == '1.3.0'
