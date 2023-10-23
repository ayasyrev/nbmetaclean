.ONESHELL:
SHELL := /bin/bash

pypi: dist
	twine upload --repository pypi dist/*

dist: clean
	python3 -m build 

clean:
	rm -rf dist