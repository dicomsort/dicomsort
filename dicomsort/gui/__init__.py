from dicomsort.gui.core import DicomSort


def run():
    app = DicomSort(0)
    app.MainLoop()


if __name__ == '__main__':
    run()
