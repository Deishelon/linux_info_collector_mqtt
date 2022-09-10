#!/bin/bash
set -eu

base_path=$(dirname "$0")
echo "Starting the linux collector service, base: ${base_path}"

pushd "$base_path" || exit

set +eu
source venv/bin/activate
set -eu

python3 linux_info_collector.py "$1"

set +eu
deactivate
set -eu

popd