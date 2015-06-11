PYTHON_SETUP_PY = python setup.py

all: clean dist

clean:
	rm -rf dist
	rm -f LICENSE.txt
	rm -f README.txt

copy_dep:
	cp ../LICENSE.txt .
	cp ../README.md .

check:
	$(PYTHON_SETUP_PY) check

sdist:
	$(PYTHON_SETUP_PY) sdist

bdist:
	$(PYTHON_SETUP_PY) bdist_wheel

dist: copy_dep check sdist bdist
