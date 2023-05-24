#!/usr/bin/bash -ex

pushd `dirname "$0"`

NC="\033[0m"
GREEN="\033[0;32m"

host="$(./get_host_ip.sh $1)"

ssh $host "miniconda3/bin/conda create -n so-vits python=3.8 -y"

ssh $host "miniconda3/bin/conda run -n so-vits pip install so-vits-svc-fork"

ssh $host "mkdir -p so-vits-ws;  mkdir -p so-vits-ws/dataset_raw"

popd
