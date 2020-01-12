test:
	py.test --verbose --cov=dicomsort --cov-report=html --cov-report=xml --cov-report=term tests

clean:
	rm -rf dist build

build: clean
	python setup.py sdist

lint:
	flake8 dicomsort/*

release:
	twine upload dist/*

release-test: build
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*
