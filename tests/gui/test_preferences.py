import io
import wx

from configobj import ConfigObj
from dicomsort.gui.preferences import MiscPanel, FileNamePanel, PreferenceDlg


class TestMiscPanel:
    def test_default_state(self, app):
        config = ConfigObj()
        panel = MiscPanel(app.frame, config)

        state = panel.GetState()

        assert state['SeriesFirst'] == 'False'
        assert state['KeepOriginal'] == 'False'
        assert state['KeepSeries'] == 'False'

    def test_update_from_config(self, app):
        config = ConfigObj()
        panel = MiscPanel(app.frame, config)

        new_config = ConfigObj({
            'Miscpanel': {
                'KeepSeries': 'False',
                'SeriesFirst': 'True',
                'KeepOriginal': 'False',
            }
        })

        panel.UpdateFromConfig(new_config)

        assert panel.keepSeries.IsChecked() is False
        assert panel.seriesFirst.IsChecked() is True
        assert panel.keepOriginal.IsChecked() is False

    def test_update_from_config_empty(self, app):
        config = ConfigObj()
        panel = MiscPanel(app.frame, config)

        new_config = ConfigObj({'Miscpanel': {}})

        panel.UpdateFromConfig(new_config)

        assert panel.keepSeries.IsChecked() is True
        assert panel.seriesFirst.IsChecked() is False
        assert panel.keepOriginal.IsChecked() is True

    def test_revert_state(self, app, tmpdir):
        # Given a configuration filename
        filename = str(tmpdir.join('config.ini'))

        # And a non-empty configuration persisted to this file
        config = ConfigObj({
            'Miscpanel': {
                'KeepSeries': 'False',
                'SeriesFirst': 'True',
                'KeepOriginal': 'False',
            }
        })
        config.filename = filename
        config.write()

        # And an empty configuration pointing to this file
        empty_config = ConfigObj()
        empty_config.filename = filename

        # And a MiscPanel object using this configuration object
        panel = MiscPanel(app.frame, config)

        # When the state is reverted to the values in the .ini file
        panel.RevertState()

        # It has the expected values
        assert panel.keepSeries.IsChecked() is False
        assert panel.seriesFirst.IsChecked() is True
        assert panel.keepOriginal.IsChecked() is False

    def test_save_state(self, app, tmpdir):
        # Given a configuration filename
        orig_filename = str(tmpdir.join('config.orig'))
        new_filename = str(tmpdir.join('config.orig'))

        # And a non-empty configuration persisted to this file
        config = ConfigObj({
            'Miscpanel': {
                'KeepSeries': 'False',
                'SeriesFirst': 'True',
                'KeepOriginal': 'False',
            }
        })
        config.filename = orig_filename
        config.write()

        # And an empty configuration pointing to this file
        empty_config = ConfigObj()
        empty_config.filename = new_filename

        # And a MiscPanel object using this configuration object
        panel = MiscPanel(app.frame, config)

        # When the state is reverted to the values in the .ini file
        panel.SaveState()

        # Verify that the two files are the same
        assert list(io.open(orig_filename)) == list(io.open(new_filename))


class TestFilenamePanel:
    def test_default_state(self, app):
        config = ConfigObj()
        panel = FileNamePanel(app.frame, config)

        state = panel.GetState()

        assert state['FilenameString'] == ''
        assert state['Selection'] == 0

    def test_update_from_config(self, app):
        config = ConfigObj()
        panel = FileNamePanel(app.frame, config)

        new_config = ConfigObj({
            'FilenameFormat': {
                'FilenameString': 'MyString',
                'Selection': 1
            }
        })

        panel.UpdateFromConfig(new_config)

        assert panel.radioBox.GetSelection() == 1
        assert panel.custom.IsEnabled() is False
        assert panel.custom.GetValue() == 'MyString'

    def test_update_from_config_no_selection(self, app):
        config = ConfigObj()
        panel = FileNamePanel(app.frame, config)

        new_config = ConfigObj({
            'FilenameFormat': {
                'FilenameString': 'MyString',
            }
        })

        panel.UpdateFromConfig(new_config)

        assert panel.radioBox.GetSelection() == 0
        assert panel.custom.IsEnabled() is False
        assert panel.custom.GetValue() == 'MyString'

    def test_update_from_config_custom(self, app):
        config = ConfigObj()
        panel = FileNamePanel(app.frame, config)

        new_config = ConfigObj({
            'FilenameFormat': {
                'FilenameString': 'MyString',
                'Selection': 2,
            }
        })

        panel.UpdateFromConfig(new_config)

        assert panel.radioBox.GetSelection() == 2
        assert panel.custom.IsEnabled() is True
        assert panel.custom.GetValue() == 'MyString'

    def test_revert_state(self, app, tmpdir):
        # Given a configuration filename
        filename = str(tmpdir.join('config.ini'))

        # And a non-empty configuration persisted to this file
        config = ConfigObj({
            'FilenameFormat': {
                'FilenameString': 'MyString',
                'Selection': 2,
            }
        })
        config.filename = filename
        config.write()

        # And an empty configuration pointing to this file
        empty_config = ConfigObj()
        empty_config.filename = filename

        # And a MiscPanel object using this configuration object
        panel = FileNamePanel(app.frame, config)

        # When the state is reverted to the values in the .ini file
        panel.RevertState()

        # It has the expected values
        assert panel.radioBox.GetSelection() == 2
        assert panel.custom.IsEnabled() is True
        assert panel.custom.GetValue() == 'MyString'

    def test_save_state(self, app, tmpdir):
        # Given a configuration filename
        orig_filename = str(tmpdir.join('config.orig'))
        new_filename = str(tmpdir.join('config.orig'))

        # And a non-empty configuration persisted to this file
        config = ConfigObj({
            'FilenameFormat': {
                'FilenameString': 'MyString',
                'Selection': 2,
            }
        })
        config.filename = orig_filename
        config.write()

        # And an empty configuration pointing to this file
        empty_config = ConfigObj()
        empty_config.filename = new_filename

        # And a MiscPanel object using this configuration object
        panel = FileNamePanel(app.frame, config)

        # When the state is reverted to the values in the .ini file
        panel.SaveState()

        # Verify that the two files are the same
        assert list(io.open(orig_filename)) == list(io.open(new_filename))


class TestPreferenceDialog:
    def empty_config(self, filename):
        config = ConfigObj({
            'Miscpanel': {},
            'FilenameFormat': {
                'FilenameString': 'filename',
            },
            'Anonymization': {
                'Fields': [],
                'Replacements': {},
            }
        })

        config.filename = filename
        config.write()

        return config

    def test_constructor(self, app, tmpdir):
        config = self.empty_config(str(tmpdir.join('config.ini')))

        dlg = PreferenceDlg(app.frame, config=config)

        assert isinstance(dlg, PreferenceDlg)

    def test_on_apply(self, app, tmpdir):
        config = self.empty_config(str(tmpdir.join('config.ini')))

        dlg = PreferenceDlg(app.frame, config=config)

        assert dlg.OnApply()
