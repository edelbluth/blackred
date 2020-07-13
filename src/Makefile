PYTHON_SETUP_PY = python setup.py

all: clean test check dist doc

clean: docclean
	rm -rf dist
	rm -rf build
	rm -f LICENSE.txt
	rm -f README
	rm -f MANIFEST
	rm -rf BlackRed.egg-info
	rm -f blackred/test/testrunner.py

copy_dep:
	cp ../LICENSE.txt .
	cp ../README.rst README

check: copy_dep
	$(PYTHON_SETUP_PY) check

sdist: copy_dep
	$(PYTHON_SETUP_PY) sdist

bdist: copy_dep
	$(PYTHON_SETUP_PY) bdist

dist: check sdist bdist

flake8test:
	(cd .. && flake8 --max-line-length=120 --max-complexity=8 --show-source --statistics src)

pytest:
	(pytest --cov=blackred -v)

rsttest: copy_dep
	rst2html.py --strict README > /dev/null

test: flake8test pytest rsttest

docclean:
	(cd ../doc && make clean)

doc:
	(cd ../doc && make html)

