#!/bin/bash -ex
pushd /home/kruall

mkdir -p model-storage
mkdir -p server-code

geesefs --iam model-storage model-storage
geesefs --iam server-code server-code

rm server.py
rm -rf lib
unzip -qq -u server-code/server.zip -d ./

python3 server.py
popd
