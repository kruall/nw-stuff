#!/usr/bin/bash -ex

pushd `dirname "$0"`

NC="\033[0m"
GREEN="\033[0;32m"

host="$(./get_host_ip.sh $1)"

echo "VM: ${1}"
echo "IP: ${host}"
ssh $host "sudo apt update"
ssh $host "sudo apt install htop git tmux -y"

ssh $host "curl -sL https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh > Miniconda3.sh"
ssh $host "bash Miniconda3.sh -b -f"
ssh $host "miniconda3/bin/conda init"

echo "Miniconda3 installed"

ssh $host "miniconda3/bin/conda create -n textgen python=3.10.9 -y" 
ssh $host "miniconda3/bin/conda run -n textgen pip3 install torch torchvision torchaudio"
ssh $host "git clone https://github.com/oobabooga/text-generation-webui"
ssh $host "miniconda3/bin/conda run -n textgen pip install -r text-generation-webui/requirements.txt"

echo "text-generation-webui installed"

ssh $host "miniconda3/bin/conda install -n textgen -c conda-forge cudatoolkit-dev -y"
ssh $host "mkdir text-generation-webui/repositories"
ssh $host "cd text-generation-webui/repositories && git clone https://github.com/oobabooga/GPTQ-for-LLaMa.git -b cuda"
ssh $host "cd text-generation-webui/repositories/GPTQ-for-LLaMa && ../../../miniconda3/bin/conda run -n textgen python setup_cuda.py install"

echo "GPTQ-for-LLaMa installed"

ssh $host "cd text-generation-webui/repositories && git clone https://github.com/johnsmith0031/alpaca_lora_4bit"
ssh $host "cd text-generation-webui/repositories/alpaca_lora_4bit && ../../../miniconda3/bin/conda run -n textgen pip install -r requirements.txt"

echo "alpaca_lora_4bit installed"

popd 

echo "${GREEN}Complete${NC}"