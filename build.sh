#!/bin/bash
rm -Rf dist build
pip install --upgrade setuptools wheel twine
python setup.py sdist bdist_wheel
python -m twine upload -u __token__ dist/*
