import os

from typing import Any, Dict, List

__version__ = '3.0.0'


# Project metadata
class Metadata:
    name: str = 'dicomsort'
    pretty_name: str = 'DICOM Sort'
    description: str = 'A DICOM Sorting Utility'
    license: str = 'MIT'
    version: str = __version__
    copyright: str = 'Copyright 2011 - 2021, Jonathan Suever'

    repository: str = 'https://github.com/dicomsort/dicomsort'
    website: str = 'https://dicomsort.com'
    download_url: str = website + '/downloads.html'
    issue_url: str = repository + '/issues/new'
    version_url: str = website + '/current'

    author: str = 'Jonathan Suever'
    author_email: str = 'suever@gmail.com'
    maintainer: str = author
    maintainer_email: str = author_email

    keywords: List[str] = [
        'dicom',
        'sorting',
        'images',
    ]

    classifiers: List[str] = [
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Intended Audience :: Science/Research',
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Physics',
        'Topic :: Software Development :: Libraries'
    ]

    @classmethod
    def readme(cls) -> str:
        d = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        with open(os.path.join(d, 'README.md')) as fid:
            return fid.read()

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        return {
            'name': cls.name,
            'version': cls.version,
            'description': cls.description,
            'long_description': cls.readme(),
            'long_description_content_type': 'text/markdown',
            'keywords': ' '.join(cls.keywords),

            'license': cls.license,
            'classifiers': cls.classifiers,

            'author': cls.author,
            'author_email': cls.author_email,
            'maintainer': cls.maintainer,
            'maintainer_email': cls.maintainer_email,

            'url': cls.website,
            'download_url': cls.download_url,
        }
