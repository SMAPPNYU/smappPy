#!/bin/sh
RET=`sed -r "s/(\s+)version='([0-9]\.[0-9]\.)([0-9]+)'/echo \"\1version='\2\$((\3+1))'\"/ge" setup.py > tempfile_version`
if ["$RET" -ne "0"]; then
    echo "Parsing command number failed, exiting"
    exit 1;
fi
rm setup.py
mv tempfile_version setup.py
git commit -am "Bump version number"
python setup.py sdist upload
