#!/usr/bin/bash -ex

pushd `dirname "$0"`/../..

NC="\033[0m"
GREEN="\033[0;32m"

host="$(./scripts/get_host_ip.sh $1)"

dataset_path="$2"
dataset_name="$3"

mkdir out

pushd out

cp -r "${dataset_path}/$dataset_name" "./$dataset_name"
zip -r ${dataset_name}.zip *

scp ${dataset_name}.zip $host:~/so-vits-ws/dataset_raw
ssh $host "cd so-vits-ws/dataset_raw; unzip ${dataset_name}.zip && rm ${dataset_name}.zip"

popd

rm -rf out

popd0

echo UPLOADED