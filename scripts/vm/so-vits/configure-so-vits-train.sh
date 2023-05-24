#!/usr/bin/bash -ex

pushd `dirname "$0"`/..

NC="\033[0m"
GREEN="\033[0;32m"

host="$(./deploy-scripts/get_host_ip.sh $1)"


ssh $host "cd so-vits-ws && ../miniconda3/bin/conda run -n so-vits svc pre-resample"
ssh $host "cd so-vits-ws && ../miniconda3/bin/conda run -n so-vits svc pre-config"
ssh $host "cd so-vits-ws && ../miniconda3/bin/conda run -n so-vits svc pre-hubert"

popd