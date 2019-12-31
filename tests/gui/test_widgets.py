from dicomsort.gui.widgets import FieldSelector


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

