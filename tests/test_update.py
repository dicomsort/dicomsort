import pytest

from dicomsort.errors import InvalidVersion
from dicomsort.update import version_tuple


class TestVersionTuple:
    def test_with_prefix(self):
        assert version_tuple('v1.2.3') == (1, 2, 3)

    def test_with_suffix(self):
        assert version_tuple('1.2.3rc1') == (1, 2, 3)

    def test_various_length(self):
        assert version_tuple('1') == (1, )
        assert version_tuple('1.2') == (1, 2)
        assert version_tuple('1.2.3') == (1, 2, 3)
        assert version_tuple('1.2.3.4') == (1, 2, 3, 4)

    def test_invalid_version(self):
        with pytest.raises(InvalidVersion):
            version_tuple('ref')

