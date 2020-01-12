import dicomsort
import wx

from tests.shared import DialogTestCase
from dicomsort.gui.widgets import errors, FieldSelector, PathEditCtrl, MultiDirDlg, AboutDlg, UpdateDlg, SeriesRemoveWarningDlg, CustomDataTable


class TestFieldSelector:
    def test_constructor(self, app):
        choices = ['one', 'two', 'three']
        selector = FieldSelector(app.frame, choices=choices)

        assert isinstance(selector, FieldSelector)

    def test_disable_all(self, app):
        selector = FieldSelector(app.frame)
        selector.DisableAll()

        for widget in selector.WidgetList():
            assert widget.IsEnabled() is False

    def test_enable_all(self, app):
        selector = FieldSelector(app.frame)
        selector.EnableAll()

        for widget in selector.WidgetList():
            assert widget.IsEnabled() is True

    def test_has_default_none_selected(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        assert selector.has_default() is False

    def test_has_default_series_description_selected(self, app):
        selector = FieldSelector(app.frame)

        # Add "SeriesDescription" to the top of the Selected list
        selector.selected.Insert('SeriesDescription', 0)

        # Add another field below "SeriesDescription"
        selector.selected.Insert('PatientName', 0)

        assert selector.has_default() is True

    def test_select_item(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        # Make sure we start with an empty list
        assert selector.selected.GetCount() == 0

        # Select the item in the options
        selector.options.SetSelection(0)

        # Trigger the SelectItem callback
        selector.SelectItem()

        # Make sure that it added this item to the selected list
        items = selector.selected.GetStrings()

        assert items == ['PatientName']

        # Select another item in the options
        selector.options.SetSelection(1)

        # Trigger the SelectItem callback
        selector.SelectItem()

        # Make sure that it added this item to the selected list
        items = selector.selected.GetStrings()

        assert items == ['PatientName', 'PatientID']

    def test_select_item_with_default(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        # Make sure we start with an empty list
        assert selector.selected.GetCount() == 0

        # Select the "default" SeriesDescription
        selector.options.SetSelection(2)

        # Trigger the SelectItem callback
        selector.SelectItem()

        assert selector.selected.GetStrings() == ['SeriesDescription']

        # Select another field
        selector.options.SetSelection(0)

        # Trigger the SelectItem callback
        selector.SelectItem()

        # SeriesDescription should remain at the bottom
        assert selector.selected.GetStrings() == ['PatientName', 'SeriesDescription']

        # Select another field
        selector.options.SetSelection(1)

        # Trigger the SelectItem callback
        selector.SelectItem()

        # SeriesDescription should remain at the bottom
        assert selector.selected.GetStrings() == ['PatientName', 'PatientID', 'SeriesDescription']

    def test_set_options(self, app):
        original_choices = ['one', 'two', 'three']
        selector = FieldSelector(app.frame, choices=original_choices)

        assert selector.options.GetStrings() == original_choices
        assert selector.choices == original_choices

        new_choices = ['four', 'five', 'six']
        selector.SetOptions(new_choices)

        assert selector.options.GetStrings() == new_choices
        assert selector.choices == new_choices

    def test_promote_selection(self, app):
        choices = ['one', 'two', 'three']
        selector = FieldSelector(app.frame, choices=choices)

        selector.selected.SetItems(choices)

        # Promote the last one
        selector.selected.SetStringSelection(choices[2])
        selector.PromoteSelection()

        assert selector.selected.GetStrings() == ['one', 'three', 'two']

        # Promote again
        selector.PromoteSelection()

        assert selector.selected.GetStrings() == ['three', 'one', 'two']

        # Try to Promote again
        selector.PromoteSelection()

        assert selector.selected.GetStrings() == ['three', 'one', 'two']

    def test_demote_selection(self, app):
        choices = ['one', 'two', 'three']
        selector = FieldSelector(app.frame, choices=choices)

        selector.selected.SetItems(choices)

        # Demote the first one
        selector.selected.SetStringSelection(choices[0])
        selector.DemoteSelection()

        assert selector.selected.GetStrings() == ['two', 'one', 'three']

        # Demote again
        selector.DemoteSelection()

        assert selector.selected.GetStrings() == ['two', 'three', 'one']

        # Try to demote again
        selector.DemoteSelection()

        assert selector.selected.GetStrings() == ['two', 'three', 'one']

    def test_promote_selection_with_default(self, app):
        choices = ['one', 'two', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        selector.selected.SetItems(choices)

        # Try to promote the default
        selector.selected.SetStringSelection(choices[2])
        selector.PromoteSelection()

        # The ordering remained unchanged
        assert selector.selected.GetStrings() == choices

    def test_deselect_item(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        selector.selected.SetItems(choices)

        selector.selected.SetStringSelection('PatientID')

        selector.DeselectItem()

        assert selector.selected.GetStrings() == ['PatientName', 'SeriesDescription']

    def test_deselect_item_no_selection(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)
        selector.selected.SetItems(choices)

        selector.DeselectItem()

        assert selector.selected.GetStrings() == choices

    def test_get_format_fields(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)
        selector.selected.SetItems(choices)

        expected = ['%(PatientName)s', '%(PatientID)s', '%(SeriesDescription)s']
        assert selector.GetFormatFields() == expected

    def test_filter(self, app):
        choices = ['PatientName', 'PatientID', 'SeriesDescription']
        selector = FieldSelector(app.frame, choices=choices)

        assert selector.options.GetStrings() == choices

        selector.Filter('atient')

        assert selector.options.GetStrings() == ['PatientName', 'PatientID']

class TestPathEditCtrl:
    def test_constructor(self, app):
        ctrl = PathEditCtrl(app.frame)

        assert isinstance(ctrl, PathEditCtrl)

    def test_set_paths_string(self, app, tmpdir):
        path = str(tmpdir)

        ctrl = PathEditCtrl(app.frame)
        ctrl.SetPaths(path)

        assert ctrl.path == [path, ]

    def test_set_paths_list(self, app, tmpdir):
        path1 = tmpdir.join('path1')
        path2 = tmpdir.join('path2')

        path1.mkdir()
        path2.mkdir()

        paths = [str(path1), str(path2)]

        ctrl = PathEditCtrl(app.frame)
        ctrl.SetPaths(paths)

        assert ctrl.path == paths

    def test_set_paths_bad_path(self, app, mocker, tmpdir):
        mock = mocker.patch.object(errors, 'throw_error')

        goodpath = str(tmpdir)

        # Paths that do not exist
        badpath1 = str(tmpdir.join('not-valid1'))
        badpath2 = str(tmpdir.join('not-valid2'))

        ctrl = PathEditCtrl(app.frame)
        ctrl.SetPaths([goodpath, badpath1, badpath2])

        mock.assert_called_once_with(
            'The Following directories are invalid paths: %s, %s' % (badpath1, badpath2),
            'Invalid Paths',
            parent=app.frame
        )

    def test_validate_path_single(self, app, tmpdir):
        path = str(tmpdir)

        ctrl = PathEditCtrl(app.frame)
        ctrl.edit.SetValue(path)
        ctrl.ValidatePath()

        assert ctrl.path == [path, ]

    def test_validate_path_multiple(self, app, tmpdir):
        path1 = tmpdir.join('path1')
        path2 = tmpdir.join('path2')

        path1.mkdir()
        path2.mkdir()

        paths = [str(path1), str(path2)]

        ctrl = PathEditCtrl(app.frame)
        ctrl.edit.SetValue(';'.join(paths))
        ctrl.ValidatePath()

        assert ctrl.path == paths


class TestMultiDirDlg(DialogTestCase):
    def test_constructor(self):
        dlg = MultiDirDlg(self.frame)
        assert isinstance(dlg, MultiDirDlg)


class TestUpdateDlg(DialogTestCase):
    def test_on_close(self):
        dlg = UpdateDlg(self.frame, '1.2.3')
        dlg.OnClose()

    def test_on_update(self, mocker):
        dlg = UpdateDlg(self.frame, '1.2.3')
        url = 'https://dicomsort.com'

        mock = mocker.patch.object(dlg.link, 'GotoURL')

        dlg.OnUpdate()

        mock.assert_called_once_with(url)


class TestAboutDialog(DialogTestCase):
    def test_constructor(self):
        dlg = AboutDlg(self.frame)

        # Just a few sanity checks
        assert dlg.info.GetVersion() == dicomsort.__version__
        assert dlg.info.GetName() == 'DICOM Sorting'
        assert dlg.info.GetWebSiteURL() == 'https://dicomsort.com'


class TestSeriesRemoveWarningDlg(DialogTestCase):
    def test_on_change(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnChange()

        assert dlg.choice == 1

    def test_on_cancel(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnCancel()

        assert dlg.choice == 0

    def test_on_accept(self):
        dlg = SeriesRemoveWarningDlg(self.frame)
        dlg.OnAccept()

        assert dlg.choice == 2


class TestCustomDataTable():
    def test_no_data(self):
        dt = CustomDataTable(None)

        assert dt.data == [['', '', ''], ]

    def test_get_number_rows(self):
        count = 4
        data = [['', '', ''], ] * count
        dt = CustomDataTable(data)

        assert dt.GetNumberRows() == count

    def test_get_number_cols(self):
        dt = CustomDataTable(None)

        assert dt.GetNumberCols() == 3

    def test_is_empty_cell(self):
        data = [['', '', ''], ['not', 'empty', 'row']]
        dt = CustomDataTable(data)

        assert dt.IsEmptyCell(0, 0) is True
        assert dt.IsEmptyCell(0, 1) is True
        assert dt.IsEmptyCell(0, 2) is True

        assert dt.IsEmptyCell(1, 0) is False
        assert dt.IsEmptyCell(1, 1) is False
        assert dt.IsEmptyCell(1, 2) is False

        # Address beyond the range of the data
        assert dt.IsEmptyCell(2, 0) is True
        assert dt.IsEmptyCell(0, 3) is True

    def test_get_value(self):
        data = [['', '', ''], ['not', 'empty', 'row']]
        dt = CustomDataTable(data)

        assert dt.GetValue(0, 0) == ''
        assert dt.GetValue(0, 1) == ''
        assert dt.GetValue(0, 2) == ''

        assert dt.GetValue(1, 0) == 'not'
        assert dt.GetValue(1, 1) == 'empty'
        assert dt.GetValue(1, 2) == 'row'

        # Address beyond the range of the data
        assert dt.GetValue(2, 0) == ''
        assert dt.GetValue(0, 3) == ''

    def test_set_value(self):
        data = [['', '', ''], ['not', 'empty', 'row']]
        dt = CustomDataTable(data)
        value = 'value'

        # Set an in-range value
        dt.SetValue(1, 0, value)

        assert dt.GetValue(1, 0) == value

        # Set an out-of-range value
        dt.SetValue(2, 0, value)

    def test_get_col_label_value(self):
        dt = CustomDataTable(None)

        assert dt.GetColLabelValue(0) == ''
        assert dt.GetColLabelValue(1) == 'DICOM Property'
        assert dt.GetColLabelValue(2) == 'Replacement Value'

    def test_get_type_name(self):
        dt = CustomDataTable(None)

        assert dt.GetTypeName(10, 0) == wx.grid.GRID_VALUE_BOOL
        assert dt.GetTypeName(10, 1) == wx.grid.GRID_VALUE_STRING
        assert dt.GetTypeName(10, 2) == wx.grid.GRID_VALUE_STRING

    def test_can_get_value_as(self):
        dt = CustomDataTable(None)

        assert dt.CanGetValueAs(10, 0, wx.grid.GRID_VALUE_BOOL) is True
        assert dt.CanGetValueAs(10, 0, wx.grid.GRID_VALUE_STRING) is False

        assert dt.CanGetValueAs(10, 1, wx.grid.GRID_VALUE_BOOL) is False
        assert dt.CanGetValueAs(10, 1, wx.grid.GRID_VALUE_STRING) is True

        assert dt.CanGetValueAs(10, 2, wx.grid.GRID_VALUE_BOOL) is False
        assert dt.CanGetValueAs(10, 2, wx.grid.GRID_VALUE_STRING) is True

    def test_can_set_value_as(self):
        dt = CustomDataTable(None)

        assert dt.CanSetValueAs(10, 0, wx.grid.GRID_VALUE_BOOL) is True
        assert dt.CanSetValueAs(10, 0, wx.grid.GRID_VALUE_STRING) is False

        assert dt.CanSetValueAs(10, 1, wx.grid.GRID_VALUE_BOOL) is False
        assert dt.CanSetValueAs(10, 1, wx.grid.GRID_VALUE_STRING) is True

        assert dt.CanSetValueAs(10, 2, wx.grid.GRID_VALUE_BOOL) is False
        assert dt.CanSetValueAs(10, 2, wx.grid.GRID_VALUE_STRING) is True
