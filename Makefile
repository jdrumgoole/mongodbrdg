#
#Make pymongo_aggregation
#
# Assumes passwords for pypi have already been configured with keyring.
#


PYPIUSERNAME="jdrumgoole"
ROOT=${HOME}/GIT/mongdb_random_data_generator

root:
	@echo "The project ROOT is '${ROOT}'"

python_bin:
	pipenv run python -c "import os;print(os.environ.get('USERNAME'))"
	which python

prod_build:clean dist test
	pipenv run twine upload --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build: clean dist test
	pipenv run twine upload --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

test_all: test_scripts
	pipenv run python setup.py test

nose:
	pipenv run which python
	pipenv run nosetests

dist:
	pipenv run python setup.py sdist

clean:
	rm -rf dist bdist sdist

pkgs:
	pipenv install pymongo keyring twine nose

init: pkgs
	pipenv run keyring set https://test.pypi.org/legacy/ ${USERNAME}
	pipenv run keyring set https://upload.pypi.org/legacy/ ${USERNAME}


