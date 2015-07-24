PYTHON_SETUP_PY = python setup.py

all: clean rsttest dist

clean:
	rm -rf dist
	rm -rf build
	rm -f LICENSE.txt
	rm -f README
	rm -f MANIFEST
	rm -rf BlackRed.egg-info

copy_dep:
	cp ../LICENSE.txt .
	cp ../README.rst README

check: copy_dep
	$(PYTHON_SETUP_PY) check

sdist: copy_dep
	$(PYTHON_SETUP_PY) sdist

bdist: copy_dep
	$(PYTHON_SETUP_PY) bdist

rsttest: copy_dep
	rst2html.py --strict README > /dev/null

dist: check sdist bdist
