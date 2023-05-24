#!/usr/bin/bash -ex

vm_name="$1"
password="$2"

pushd `dirname "$0"`

echo "$password" | sudo -S apt update
echo "$password" | sudo -S sudo apt install build-essential htop git tmux -y

pushd $HOME

curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh > Miniconda3.sh
bash Miniconda3.sh -b -f
~/miniconda3/bin/conda init

popd

source ~/.bashrc

next_init=init-wsl-${vm_name}.sh

if [ -f ../${vm_name}/$next_init ] ; then
    ../${vm_name}/$next_init
fi

popd

