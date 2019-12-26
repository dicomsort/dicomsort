import os

from os.path import expanduser

configuration_version = '2.0'

default_filename = '%(ImageType)s (%(InstanceNumber)04d)%(FileExtension)s'

default_configuration = {
    'Version': configuration_version,
    'Anonymization': {
        'Fields': [
            'OtherPatientsIDS',
            'PatientID',
            'PatientBirthDate',
            'PatientName',
            'ReferringPhysiciansName',
            'RequestingPhysician'
        ],
        'Replacements': {
            'PatientName': 'ANONYMOUS',
            'PatientID': '%(PatientName)s'
        }
    },
    'FilenameFormat': {
        'FilenameString': default_filename,
        'Selection': 0
    },
    'Miscpanel': {
        'KeepSeries': 'True',
        'SeriesFirst': 'False',
        'KeepOriginal': 'True'
    }
}

if os.name == 'nt':
    configuration_file = os.path.join(expanduser('~'), 'dicomSort.ini')
else:
    configuration_file = os.path.join(os.getenv('HOME'), '.dicomSort.ini')
