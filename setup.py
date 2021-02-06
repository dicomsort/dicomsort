import dicomsort
import os

from setuptools import find_packages, setup

metadata = dicomsort.Metadata

if __name__ == '__main__':
    setup(
        **metadata.to_dict(),
        packages=find_packages(),
        install_requires=[
            'configobj >= 5.0.0',
            'pydicom >= 2.0.0',
            'wxpython >= 4.0.0',
        ],
        zip_safe=False,
        scripts=[
            os.path.join('bin', 'dicomsort')
        ],
    )
