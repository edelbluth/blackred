PYTHON_SETUP_PY = python setup.py

all: clean dist

clean:
	rm -rf dist
	rm -rf build
	rm -f LICENSE.txt
	rm -f README
	rm -f MANIFEST

copy_dep:
	cp ../LICENSE.txt .
	cp ../README.rst README

check:
	$(PYTHON_SETUP_PY) check

sdist:
	$(PYTHON_SETUP_PY) sdist

bdist:
	$(PYTHON_SETUP_PY) bdist

dist: copy_dep check sdist bdist
