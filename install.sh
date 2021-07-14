#!/usr/bin/env bash
mamba install -y pytorch torchvision torchaudio cudatoolkit=11.1 fastai -c fastchan -c pytorch -c nvidia
mamba install -y -c conda-forge jupyter_nbextensions_configurator

pushd .
cd ../fastcore
pip install -e ".[dev]"
cd ../fastai
pip install -e ".[dev]"
popd
#reinstall numpy due to pandas incompatability
pip uninstall numpy
pip install numpy 
#forces lower version of pytorch pip install git+https://github.com/openai/CLIP.git
