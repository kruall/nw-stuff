#!/usr/bin/bash -ex

pushd $HOME

miniconda3/bin/conda create -n textgen python=3.10.9 -y
miniconda3/bin/conda run -n textgen pip install torch torchvision torchaudio
git clone https://github.com/oobabooga/text-generation-webui
miniconda3/bin/conda run -n textgen pip install -r text-generation-webui/requirements.txt

echo "text-generation-webui installed"

miniconda3/bin/conda install -n textgen -c conda-forge cudatoolkit-dev -y
mkdir text-generation-webui/repositories

pushd text-generation-webui/repositories
git clone https://github.com/oobabooga/GPTQ-for-LLaMa.git -b cuda

pushd GPTQ-for-LLaMa
../../../miniconda3/bin/conda run -n textgen python setup_cuda.py install
popd

echo "GPTQ-for-LLaMa installed"

git clone https://github.com/johnsmith0031/alpaca_lora_4bit
pushd alpaca_lora_4bit
../../../miniconda3/bin/conda run -n textgen pip install -r requirements.txt
popd

echo "alpaca_lora_4bit installed"

popd

echo 'conda activate textgen' >> ~/.bashrc

popd 
