#!/usr/bin/env bash
set -e
export PROJECT_NAME="hootingyard"
eval "$(conda shell.bash hook)"
conda create -y -n $PROJECT_NAME python==3.9
eval conda activate $PROJECT_NAME
which python
python -m pip install -r src/requirements_dev.txt -r src/requirements.txt
python -m pip install -e src
