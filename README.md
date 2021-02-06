# DICOM Sort

[![CircleCI](https://circleci.com/gh/dicomsort/dicomsort.svg?style=svg)](https://circleci.com/gh/dicomsort/dicomsort)
[![Maintainability](https://api.codeclimate.com/v1/badges/9814e4a5f1881ec25922/maintainability)](https://codeclimate.com/github/suever/dicomsort/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/9814e4a5f1881ec25922/test_coverage)](https://codeclimate.com/github/suever/dicomsort/test_coverage)
[![PyPi version](https://pypip.in/v/dicomsort/badge.png)](https://pypi.org/project/dicomsort/)

DICOM Sort is a utility that takes a series of DICOM images stored within an
arbitrary directory structure and sorts them into a directory tree based upon
the value of selected DICOM fields.

## Installation

### Binary Installers

Binary distributions for Windows and Mac OS are available at [the project
website](https://dicomsort.com).

### Installation via `pip`

DICOM Sort is available as [`dicomsort`](https://pypi.org/project/dicomsort/) on
the [Python Package Index (pypi)](https://pypi.org) and can therefore easily be
installed with [`pip`](https://pypi.org/project/pip/).

```bash
pip install dicomsort
```

After installation, DICOM Sort can be launched with simply the `dicomsort` command line script:

```bash
dicomsort
```

### Installation via `setuptools`

To install from source, first clone the git repository

```bash
git clone https://github.com/suever/dicomsort.git
```

Install the `dicomsort` script using the project's `setup.py` file. This will automatically install all project dependencies

```bash
cd dicomsort
python setup.py install
```

## Development

For running tests, you will want to install the required development dependencies using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

For running tests, we use `pytest`. These can be run reproducibly using the provided `Makefile`

```bash
make test
```

## Contributing
If you have any questions or would like to request a feature, feel free to 
provide feedback via the [Github Issues](https://github.com/suever/dicomsort/issues) page.

## License
This software is licensed under the MIT License
Copyright (C) 2011 - 2021  Jonathan Suever
