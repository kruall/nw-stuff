#!/usr/bin/bash -ex

pushd $HOME

miniconda3/bin/conda create -n langchain -y
echo 'conda activate langchain' >> ~/.bashrc

miniconda3/bin/conda install -n langchain pip -y
miniconda3/bin/conda run -n langchain pip install jupyter jupyterlab
miniconda3/bin/conda run -n langchain pip install --user ipykernel
miniconda3/bin/conda run -n langchain python -m ipykernel install --name langchain --user
miniconda3/bin/conda run -n langchain pip install langchain pandas tiktoken huggingface_hub

git clone https://github.com/paolorechia/learn-langchain
miniconda3/bin/conda run -n langchain pip install -r learn-langchain/requirements.txt

popd