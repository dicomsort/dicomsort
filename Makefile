test:
	coverage run --source=dicomsort -m pytest --verbose
	coverage report
	coverage html
	coverage xml

clean:
	rm -rf dist build

build: clean
	python setup.py sdist

lint:
	flake8 dicomsort/*

release: build
	twine upload --repository-url https://upload.pypi.org/legacy/ dist/*

release-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

exe: clean
	python misc/cx_setup.py bdist_msi

dmg: clean
	python misc/cx_setup.py bdist_dmg
