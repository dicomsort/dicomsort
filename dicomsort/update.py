import re
import requests

import dicomsort
from dicomsort.errors import InvalidVersion

GITHUB_RELEASE_API = 'https://api.github.com/repos/%(repo)s/releases/latest'
VERSION_REGEX = re.compile('^v?(\\d(\\.\\d+)*)')


def latest_release():
    """Retrieve latest release name from Github."""
    try:
        url = GITHUB_RELEASE_API % {'repo': dicomsort.__repository__}
        resp = requests.get(url)

        if not resp.ok:
            return None

        return resp.json()['tag_name']
    except Exception:
        return None


def version_tuple(ver):
    match = VERSION_REGEX.match(ver)

    if match is None:
        raise InvalidVersion('{} is not a valid version string'.format(ver))

    parsed_version = match.groups()[0]

    return tuple(int(x) for x in parsed_version.split('.'))


CURRENT_VERSION_TUPLE = version_tuple(dicomsort.__version__)


def update_available():
    # First try to see if we can connect
    latest = latest_release()

    if latest is None:
        return False, None

    # Break it up to see if it's a dev version
    latest_version_tuple = version_tuple(latest)
    for ind in range(len(latest_version_tuple)):
        if latest_version_tuple[ind] > CURRENT_VERSION_TUPLE[ind]:
            return True, latest

        return False, None
