import unittest
from dicomsort import config


class TestConfig(unittest.TestCase):
    def test_configuration_version(self):
        assert config.configuration_version == '2.0'

    def test_default_configuration(self):
        default = config.default_configuration

        # Version
        assert 'Version' in default
        assert default['Version'] == config.configuration_version

        # Anonymization
        assert 'Anonymization' in default
        anon = default['Anonymization']
        assert isinstance(anon, dict)

        assert 'Fields' in anon
        assert isinstance(anon['Fields'], list)

        assert 'Replacements' in anon
        assert isinstance(anon['Replacements'], dict)

        # Filename Format
        assert 'FilenameFormat' in default
        assert isinstance(default['FilenameFormat'], dict)

        # Miscellaneous Settings
        assert 'Miscpanel' in default
        assert isinstance(default['Miscpanel'], dict)
