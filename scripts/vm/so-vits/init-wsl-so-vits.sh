#!/usr/bin/bash -ex

pushd $HOME

echo 'export LD_LIBRARY_PATH="${LD_LIBRARY_PATH}":/usr/lib/wsl/lib/' >> ~/.bashrc

miniconda3/bin/conda create -n so-vits python=3.8 -y
echo 'conda activate so-vits' >> ~/.bashrc

git clone "https://github.com/svc-develop-team/so-vits-svc.git"

miniconda3/bin/conda run -n so-vits pip install -r so-vits-svc/requirements.txt

popd