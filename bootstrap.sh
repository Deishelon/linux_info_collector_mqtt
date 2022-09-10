#!/bin/bash
set -eu

echo "Starting the linux collector service"
source venv/bin/activate
python3 linux_info_collector.py "$1"
