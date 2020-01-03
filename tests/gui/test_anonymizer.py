from dicomsort.gui.anonymizer import AnonymizeList


class TestAnonymizeList:
    def test_constructor(self, app):
        a = AnonymizeList(app.frame)

        assert isinstance(a, AnonymizeList)

    def test_set_replacement_dict_valid_fields(self, app):
        a = AnonymizeList(app.frame)
        d = {
            'Field': 'Value'
        }

        # Ensure that the field to replace exists in the list
        a.SetStringItems(d.keys())

        a.SetReplacementDict(d)

        # Ensure that the specified value was added to the second column
        assert a.GetStringItem(0, 1) == 'Value'

    def test_set_replacement_dict_invalid_field(self, app):
        a = AnonymizeList(app.frame)

        d = {
            'Invalid': 'value'
        }

        # A control initialized with fields not in our dict
        a.SetStringItems(['Field'])

        a.SetReplacementDict(d)

        assert a.GetStringItem(0, 1) == ''
        assert a.ItemCount == 1

    def test_get_replacement_dict(self, app):
        a = AnonymizeList(app.frame)

        fields = {
            'Field1': 'Replacement1',
            'Field2': 'Replacement2',
            'Field3': '',
        }

        a.SetStringItems(fields.keys())
        a.SetReplacementDict(fields)

        expected = {
            'Field1': 'Replacement1',
            'Field2': 'Replacement2',
        }
        d = a.GetReplacementDict()
        assert d == expected

    def test_get_anon_dict(self, app):
        a = AnonymizeList(app.frame)

        fields = {
            'Field1': 'Replacement1',
            'Field2': 'Replacement2',
            'Field3': '',
        }

        keys = fields.keys()
        keys.sort()

        a.SetStringItems(keys)
        a.SetReplacementDict(fields)

        # Check fields 2 and 3
        a.CheckItems([1, 2])

        expected = {
            'Field2': 'Replacement2',
            'Field3': '',
        }

        assert a.GetAnonDict() == expected

    def test_get_dicom_field(self, app):
        a = AnonymizeList(app.frame)

        # Add a field
        a.SetStringItems(['PatientName', 'PatientID'])

        assert a.GetDicomField(0) == 'PatientName'
        assert a.GetDicomField(1) == 'PatientID'
