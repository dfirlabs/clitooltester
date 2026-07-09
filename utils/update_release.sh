#!/bin/bash
#
# Script that makes changes in preparation of a new release, such as updating
# the version and documentation.

VERSION=`date -u +"%Y%m%d"`

# Update the Python module version.
sed "s/__version__ = '[0-9]*'/__version__ = '${VERSION}'/" -i clitooltester/__init__.py

# Regenerate the API documentation.
tox -edocs
