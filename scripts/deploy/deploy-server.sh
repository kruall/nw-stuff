#!/usr/bin/bash -ex

pushd `dirname "$0"`/../..

if [ -f scripts/variables.sh ] ; then
    . scripts/variables.sh
else
    echo "WARN: can't find the file with variables by path '$(readlink -f scripts/variables.sh)'"
fi

mkdir -p out
mkdir -p out/server
rm -rf out/server/*
cp -r bot/server/* out/server/
cp -r bot/lib out/server/
pushd out/server/
zip -r server.zip *
mv server.zip ../
popd

pushd bot

python3 code-uploader.py ../out/server.zip

popd


rm -rf out

popd


