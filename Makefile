.PHONY: build check install dist srpm rpm pypi clean

NAME = object-validator
RPM_NAME := python-$(NAME)
PYTHON := python

build:
	$(PYTHON) setup.py build

check:
	$(PYTHON) setup.py test

install:
	$(PYTHON) setup.py install --skip-build $(INSTALL_FLAGS)

dist:
	$(PYTHON) setup.py sdist
	mv dist/$(NAME)-*.tar.gz .

srpm: dist
	rpmbuild -bs --define "_sourcedir $(CURDIR)" $(RPM_NAME).spec

rpm: dist
	rpmbuild -ba --define "_sourcedir $(CURDIR)" $(RPM_NAME).spec

pypi: clean
	$(PYTHON) setup.py sdist upload

clean:
	rm -rf build dist $(NAME)-*.tar.gz object_validator.egg-info
