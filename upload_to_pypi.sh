#!/bin/sh
sed -r "s/(\s+)version='([0-9]\.[0-9]\.)([0-9]+)'/echo \"\1version='\2\$((\3+1))'\"/ge" setup.py > tempfile_version
rm setup.py
mv tempfile_version setup.py
git commit -am "Bump version number"
python setup.py sdist upload
