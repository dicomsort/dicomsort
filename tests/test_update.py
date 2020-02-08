import pytest

import dicomsort
from dicomsort.errors import InvalidVersion
from dicomsort.update import version_tuple, latest_release, GITHUB_RELEASE_API, update_available


class TestLatestRelease:
    URL = GITHUB_RELEASE_API % {'repo': dicomsort.__repository__}

    def test_happy_path(self, requests_mock):
        version = 'v1.2.3'
        requests_mock.get(self.URL, json={'tag_name': version})

        assert latest_release() == version

    def test_invalid_payload(self, requests_mock):
        requests_mock.get(self.URL, json={})

        assert latest_release() is None

    def test_404(self, requests_mock):
        requests_mock.get(self.URL, status_code=404)

        assert latest_release() is None


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


class TestUpdateAvailable:
    URL = GITHUB_RELEASE_API % {'repo': dicomsort.__repository__}

    def test_new_version(self, requests_mock):
        version = 'v100.0.0'
        requests_mock.get(self.URL, json={'tag_name': version})

        assert update_available() == (True, version)

    def test_old_version(self, requests_mock):
        version = 'v0.0.0.'
        requests_mock.get(self.URL, json={'tag_name': version})

        assert update_available() == (False, None)

    def test_no_version(self, requests_mock):
        requests_mock.get(self.URL, status_code=404)

        assert update_available() == (False, None)

