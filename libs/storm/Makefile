PYTHON ?= python
PYDOCTOR ?= pydoctor
PGPORT ?= 5432

TEST_COMMAND = $(PYTHON) setup.py test

STORM_POSTGRES_URI = postgres:storm_test
STORM_POSTGRES_HOST_URI = postgres://localhost:$(PGPORT)/storm_test
STORM_MYSQL_URI = mysql:storm_test
STORM_MYSQL_HOST_URI = mysql://localhost/storm_test

export STORM_POSTGRES_URI
export STORM_POSTGRES_HOST_URI
export STORM_MYSQL_URI
export STORM_MYSQL_HOST_URI

all: build

build:
	$(PYTHON) setup.py build_ext -i

develop:
	$(TEST_COMMAND) --quiet --dry-run

check:
	@ # Run the tests once with C extensions and once without them.
	STORM_CEXTENSIONS=0 $(TEST_COMMAND)
	STORM_CEXTENSIONS=1 $(TEST_COMMAND)

check-with-trial: develop
	STORM_TEST_RUNNER=trial STORM_CEXTENSIONS=0 $(PYTHON) test
	STORM_TEST_RUNNER=trial STORM_CEXTENSIONS=1 $(PYTHON) test

doc:
	$(PYDOCTOR) --make-html --html-output apidoc --add-package storm

release:
	$(PYTHON) setup.py sdist

clean:
	rm -rf build
	rm -rf build-stamp
	rm -rf dist
	rm -rf storm.egg-info
	rm -rf debian/files
	rm -rf debian/python-storm
	rm -rf debian/python-storm.*
	rm -rf *.egg
	rm -rf _trial_temp
	find . -name "*.so" -type f -exec rm -f {} \;
	find . -name "*.pyc" -type f -exec rm -f {} \;
	find . -name "*~" -type f -exec rm -f {} \;

.PHONY: all build check clean develop doc release
