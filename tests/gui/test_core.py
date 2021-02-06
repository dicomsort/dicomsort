import os

from dicomsort.gui.core import MainFrame, sys, wx, errors
from dicomsort.gui.events import CounterEvent, SortEvent, PathEvent
from tests.shared import WxTestCase


class TestMainFrame(WxTestCase):
    def test_on_quit(self, mocker):
        mock = mocker.patch.object(sys, 'exit')
        frame = MainFrame(self.frame)
        frame.Show()

        frame.Close()

        # Ensure that the program was exited
        mock.assert_called_once_with(0)

    def test_on_count(self, mocker):
        mocker.patch.object(sys, 'exit')
        frame = MainFrame(self.frame)
        frame.Show()

        mock = mocker.patch.object(frame, 'SetStatusText')

        event = CounterEvent(
            Count=2,
            total=42,
        )

        frame.OnCount(event)
        mock.assert_called_once_with('2 / 42')

        frame.Close()

    def test_on_about(self, mocker):
        mocker.patch.object(sys, 'exit')
        frame = MainFrame(self.frame)
        frame.Show()

        frame.OnAbout()

        frame.Close()

    def test_on_help(self, mocker):
        mocker.patch.object(sys, 'exit')
        frame = MainFrame(self.frame)
        frame.Show()

        frame.OnHelp()

        frame.Close()

    def test_sort_not_anonymous(self, mocker, dicom_generator, tmpdir):
        mocker.patch.object(sys, 'exit')

        filename, _ = dicom_generator(
            'image.dcm',
            SeriesDescription='description',
            SeriesNumber=1
        )

        input_directory = os.path.basename(filename)

        output_directory = str(tmpdir.join('output'))

        frame = MainFrame(self.frame)

        frame.dicom_sorter.pathname = [input_directory, ]

        mocker.patch.object(
            frame, 'SelectOutputDir', return_value=output_directory
        )

        frame.Show()
        event = SortEvent(
            anon=False,
            fields=[
                'SeriesDescription'
            ]
        )

        wx.PostEvent(frame, event)

        frame.Sort(event)

        for sorter in frame.dicom_sorter.sorters:
            sorter.join()

    def test_sort_anonymous(self, mocker, dicom_generator, tmpdir):
        mocker.patch.object(sys, 'exit')

        filename, _ = dicom_generator(
            'image.dcm',
            SeriesDescription='description',
            SeriesNumber=1
        )

        input_directory = os.path.basename(filename)

        output_directory = str(tmpdir.join('output'))

        frame = MainFrame(self.frame)

        frame.dicom_sorter.pathname = [input_directory, ]

        mocker.patch.object(
            frame, 'SelectOutputDir', return_value=output_directory
        )

        frame.Show()
        event = SortEvent(
            anon=True,
            fields=[
                'SeriesDescription'
            ]
        )

        wx.PostEvent(frame, event)

        frame.Sort(event)

        for sorter in frame.dicom_sorter.sorters:
            sorter.join()

    def test_fill_list(self, dicom_generator, mocker):
        filename, dcm = dicom_generator(
            SeriesDescription='desc',
            SeriesNumber=1
        )

        mocker.patch.object(sys, 'exit')

        input_directory = os.path.dirname(filename)

        frame = MainFrame(self.frame)
        frame.Show()

        event = PathEvent(path=[input_directory, ])

        frame.FillList(event)

        assert frame.selector.options.GetStrings() == dcm.dir('')

        frame.Close()

    def test_fill_list_invalid(self, mocker, tmpdir):
        filename = tmpdir.join('output')
        filename.write('invalid')

        mocker.patch.object(sys, 'exit')

        mock = mocker.patch.object(errors, 'throw_error')

        input_directory = os.path.basename(str(filename))

        frame = MainFrame(self.frame)
        frame.Show()

        event = PathEvent(path=[input_directory, ])

        frame.FillList(event)

        mock.assert_called_once_with(
            'output contains no DICOMs',
            'No DICOMs Present',
            parent=frame
        )

        frame.Close()
