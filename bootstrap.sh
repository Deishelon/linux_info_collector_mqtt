#!/bin/bash
set -eu

base_path=$(dirname "$0")
echo "Starting the linux collector service, base: ${base_path}"

pushd "$base_path"
source venv/bin/activate
python3 linux_info_collector.py "$1"
deactivate
popd